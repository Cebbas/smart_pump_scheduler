"""Price fetching logic for Pollen Pump."""
from __future__ import annotations

import logging
from datetime import datetime, date
from typing import Optional
import aiohttp

from .const import (
    NORDPOOL_API_URL,
    NORDPOOL_API_CURRENCY_MAP,
)

_LOGGER = logging.getLogger(__name__)


async def fetch_nordpool_prices(
    area: str,
    currency: str,
    vat: bool,
    session: aiohttp.ClientSession,
    for_date: Optional[date] = None,
) -> dict[int, float] | None:
    """
    Fetch hourly prices from Nordpool API.
    Returns dict {hour(0-23): price_in_ore_per_kwh} or None on failure.
    """
    if for_date is None:
        for_date = date.today()

    date_str = for_date.strftime("%Y-%m-%d")

    params = {
        "market": "DayAhead",
        "deliveryArea": area,
        "currency": NORDPOOL_API_CURRENCY_MAP.get(currency, "SEK"),
        "date": date_str,
    }

    try:
        async with session.get(NORDPOOL_API_URL, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status != 200:
                _LOGGER.warning("Nordpool API returned status %s", resp.status)
                return None

            data = await resp.json()
            prices = _parse_nordpool_response(data, currency, vat)
            return prices

    except aiohttp.ClientError as e:
        _LOGGER.error("Network error fetching Nordpool prices: %s", e)
        return None
    except Exception as e:
        _LOGGER.error("Unexpected error fetching Nordpool prices: %s", e)
        return None


def _parse_nordpool_response(data: dict, currency: str, vat: bool) -> dict[int, float] | None:
    """Parse Nordpool API response into {hour: price_ore_kwh}."""
    try:
        rows = data.get("multiAreaEntries", [])
        if not rows:
            _LOGGER.warning("No price data in Nordpool response")
            return None

        prices = {}
        for entry in rows:
            delivery_start = entry.get("deliveryStart", "")
            if not delivery_start:
                continue
            hour = datetime.fromisoformat(delivery_start.replace("Z", "+00:00")).hour
            entry_prices = entry.get("entryPerArea", {})
            price_mwh = None
            for area_key, val in entry_prices.items():
                price_mwh = val
                break

            if price_mwh is None:
                continue

            # Convert MWh → kWh (divide by 1000)
            price_kwh = price_mwh / 1000

            # Convert EUR → SEK/NOK if needed (Nordpool returns in selected currency)
            # VAT: SE = 25%, NO = 25%, DK = 25%, FI = 24%
            if vat:
                price_kwh *= 1.25

            # Convert to öre if SEK/NOK
            if currency in ("SEK", "NOK", "DKK"):
                price_kwh *= 100  # kr → öre

            prices[hour] = round(price_kwh, 2)

        return prices if prices else None

    except Exception as e:
        _LOGGER.error("Error parsing Nordpool response: %s", e)
        return None


def get_price_from_sensor(hass, entity_id: str) -> float | None:
    """Read current price from a HA sensor entity."""
    state = hass.states.get(entity_id)
    if state is None or state.state in ("unavailable", "unknown"):
        _LOGGER.warning("Price sensor %s is unavailable", entity_id)
        return None
    try:
        return float(state.state)
    except ValueError:
        _LOGGER.error("Could not parse price from sensor %s: %s", entity_id, state.state)
        return None


def get_hourly_prices_from_sensor(hass, entity_id: str) -> dict[int, float] | None:
    """
    Try to extract 24-hour price forecast from a sensor.
    Works with Nordpool integration and Tibber sensors that expose
    hourly prices as attributes.
    Returns {hour: price} or None.
    """
    state = hass.states.get(entity_id)
    if state is None:
        return None

    attrs = state.attributes

    # Nordpool integration format
    if "raw_today" in attrs:
        try:
            raw = attrs["raw_today"]
            prices = {}
            for entry in raw:
                hour = entry["start"].hour
                prices[hour] = float(entry["value"])
            return prices
        except Exception as e:
            _LOGGER.warning("Could not parse raw_today from %s: %s", entity_id, e)

    # Tibber format
    if "today" in attrs:
        try:
            today = attrs["today"]
            return {i: float(v) for i, v in enumerate(today)}
        except Exception as e:
            _LOGGER.warning("Could not parse today from %s: %s", entity_id, e)

    # Fallback: use current value for all hours
    try:
        current = float(state.state)
        return {h: current for h in range(24)}
    except ValueError:
        return None
