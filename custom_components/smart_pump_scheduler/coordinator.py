"""Coordinator for Smart Pump Scheduler – manages prices, schedule and pause state."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import async_track_time_change, async_call_later
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_PRICE_SOURCE,
    CONF_PRICE_SENSOR,
    CONF_SWITCH_ENTITY,
    CONF_ENABLE_PAUSE,
    CONF_PAUSE_DURATION,
    CONF_MAX_PAUSES,
    CONF_ENERGY_SOURCE,
    CONF_ENERGY_SENSOR,
    CONF_MANUAL_WATT,
    CONF_NORDPOOL_AREA,
    CONF_NORDPOOL_CURRENCY,
    CONF_NORDPOOL_VAT,
    PRICE_SOURCE_NORDPOOL,
    PRICE_SOURCE_SENSOR,
    ENERGY_SOURCE_SENSOR,
    ENERGY_SOURCE_MANUAL,
    COORDINATOR_UPDATE_INTERVAL,
    PRICE_RETRY_INTERVAL,
)
from .price_fetcher import fetch_nordpool_prices, get_hourly_prices_from_sensor
from .scheduler import build_schedule, find_next_available_hour, get_savings

_LOGGER = logging.getLogger(__name__)


class SmartPumpSchedulerCoordinator(DataUpdateCoordinator):
    """Manages all state for one Smart Pump Scheduler instance."""

    def __init__(self, hass: HomeAssistant, config: dict):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=COORDINATOR_UPDATE_INTERVAL),
        )
        self.config = config
        self._prices: dict[int, float] = {}
        self._scheduled_hours: list[int] = []
        self._paused_hours: set[int] = set()
        self._pause_count_today: int = 0
        self._is_paused: bool = False
        self._pause_end_time: datetime | None = None
        self._energy_today_kwh: float = 0.0
        self._cost_today: float = 0.0
        self._last_energy_reading: float | None = None
        self._session: aiohttp.ClientSession | None = None
        self._unsub_midnight = None
        self._unsub_hourly = None

    async def async_setup(self):
        """Set up listeners after HA starts."""
        # Rebuild schedule at 00:05 every day
        self._unsub_midnight = async_track_time_change(
            self.hass, self._handle_midnight, hour=0, minute=5, second=0
        )
        # Check schedule every hour on the hour
        self._unsub_hourly = async_track_time_change(
            self.hass, self._handle_hourly, minute=0, second=0
        )
        # Initial fetch
        await self._fetch_prices_and_build_schedule()

    async def async_teardown(self):
        """Remove listeners on unload."""
        if self._unsub_midnight:
            self._unsub_midnight()
        if self._unsub_hourly:
            self._unsub_hourly()
        if self._session and not self._session.closed:
            await self._session.close()

    # ------------------------------------------------------------------
    # Core schedule logic
    # ------------------------------------------------------------------

    async def _fetch_prices_and_build_schedule(self, retry: int = 0):
        """Fetch prices and compute today's schedule."""
        prices = await self._get_prices()

        if not prices:
            if retry < 8:  # retry for up to 2 hours
                _LOGGER.info("Prices not available, retrying in %d min", PRICE_RETRY_INTERVAL)
                async_call_later(
                    self.hass,
                    PRICE_RETRY_INTERVAL * 60,
                    lambda _: self.hass.async_create_task(
                        self._fetch_prices_and_build_schedule(retry + 1)
                    ),
                )
                return
            else:
                _LOGGER.warning("Could not fetch prices after retries, using empty schedule")
                prices = {}

        self._prices = prices
        self._scheduled_hours = build_schedule(
            prices=prices,
            config=self.config,
            paused_hours=self._paused_hours,
        )
        await self._apply_schedule()
        await self.async_refresh()

    async def _get_prices(self) -> dict[int, float]:
        """Fetch prices from configured source."""
        source = self.config.get(CONF_PRICE_SOURCE, PRICE_SOURCE_NORDPOOL)

        if source == PRICE_SOURCE_NORDPOOL:
            if self._session is None or self._session.closed:
                self._session = aiohttp.ClientSession()
            return await fetch_nordpool_prices(
                area=self.config.get(CONF_NORDPOOL_AREA, "SE3"),
                currency=self.config.get(CONF_NORDPOOL_CURRENCY, "SEK"),
                vat=self.config.get(CONF_NORDPOOL_VAT, True),
                session=self._session,
            ) or {}

        elif source == PRICE_SOURCE_SENSOR:
            entity_id = self.config.get(CONF_PRICE_SENSOR)
            if entity_id:
                return get_hourly_prices_from_sensor(self.hass, entity_id) or {}

        return {}

    async def _apply_schedule(self):
        """Turn pump on or off based on current schedule."""
        now = dt_util.now()
        current_hour = now.hour
        switch_entity = self.config.get(CONF_SWITCH_ENTITY)
        if not switch_entity:
            return

        should_run = (
            current_hour in self._scheduled_hours
            and not self._is_paused
        )

        service = "turn_on" if should_run else "turn_off"
        await self.hass.services.async_call(
            "switch", service, {"entity_id": switch_entity}, blocking=False
        )
        _LOGGER.debug("Pump %s (hour %d, scheduled=%s, paused=%s)",
                      service, current_hour, self._scheduled_hours, self._is_paused)

    # ------------------------------------------------------------------
    # Time-based callbacks
    # ------------------------------------------------------------------

    @callback
    def _handle_midnight(self, now: datetime):
        """Called at 00:05 – reset daily state and rebuild schedule."""
        self._paused_hours = set()
        self._pause_count_today = 0
        self._is_paused = False
        self._energy_today_kwh = 0.0
        self._cost_today = 0.0
        self._last_energy_reading = None
        self.hass.async_create_task(self._fetch_prices_and_build_schedule())

    @callback
    def _handle_hourly(self, now: datetime):
        """Called every hour – apply schedule and track energy."""
        self.hass.async_create_task(self._apply_schedule())
        self.hass.async_create_task(self._update_energy())
        self.hass.async_create_task(self.async_refresh())

    # ------------------------------------------------------------------
    # Pause logic
    # ------------------------------------------------------------------

    async def async_pause(self, minutes: int | None = None):
        """Pause the pump for a number of minutes."""
        if minutes is None:
            minutes = int(self.config.get(CONF_PAUSE_DURATION, 60))

        max_pauses = int(self.config.get(CONF_MAX_PAUSES, 3))
        if self._pause_count_today >= max_pauses:
            _LOGGER.warning("Max pauses (%d) reached for today", max_pauses)
            return False

        if not self.config.get(CONF_ENABLE_PAUSE, True):
            _LOGGER.info("Pause function is disabled")
            return False

        now = dt_util.now()
        current_hour = now.hour

        # Mark current hour as paused
        self._paused_hours.add(current_hour)
        self._pause_count_today += 1
        self._is_paused = True
        self._pause_end_time = now + timedelta(minutes=minutes)

        # Turn off pump immediately
        switch_entity = self.config.get(CONF_SWITCH_ENTITY)
        if switch_entity:
            await self.hass.services.async_call(
                "switch", "turn_off", {"entity_id": switch_entity}, blocking=False
            )

        # Find compensation hour
        extra = find_next_available_hour(
            prices=self._prices,
            scheduled_hours=self._scheduled_hours,
            paused_hour=current_hour,
            config=self.config,
            now=now,
        )
        if extra is not None:
            self._scheduled_hours.append(extra)
            self._scheduled_hours.sort()
            _LOGGER.info("Added compensation hour %d for paused hour %d", extra, current_hour)
        else:
            _LOGGER.info("No compensation hour available for pause")

        # Remove paused hour from schedule
        if current_hour in self._scheduled_hours:
            self._scheduled_hours.remove(current_hour)

        # Schedule resume
        async_call_later(
            self.hass,
            minutes * 60,
            lambda _: self.hass.async_create_task(self.async_resume()),
        )

        await self.async_refresh()
        return True

    async def async_resume(self):
        """Resume pump after pause."""
        self._is_paused = False
        self._pause_end_time = None
        await self._apply_schedule()
        await self.async_refresh()

    async def async_force_reschedule(self):
        """Force a full schedule recalculation."""
        await self._fetch_prices_and_build_schedule()

    # ------------------------------------------------------------------
    # Energy tracking
    # ------------------------------------------------------------------

    async def _update_energy(self):
        """Update energy and cost counters."""
        now = dt_util.now()
        current_hour = now.hour
        source = self.config.get(CONF_ENERGY_SOURCE)

        kwh = 0.0

        if source == ENERGY_SOURCE_SENSOR:
            entity_id = self.config.get(CONF_ENERGY_SENSOR)
            if entity_id:
                state = self.hass.states.get(entity_id)
                if state and state.state not in ("unavailable", "unknown"):
                    try:
                        reading = float(state.state)
                        unit = state.attributes.get("unit_of_measurement", "W")
                        if unit == "kWh":
                            if self._last_energy_reading is not None:
                                kwh = max(0.0, reading - self._last_energy_reading)
                            self._last_energy_reading = reading
                        elif unit in ("W", "kW"):
                            watts = reading if unit == "W" else reading * 1000
                            kwh = watts / 1000  # 1 hour
                    except ValueError:
                        pass

        elif source == ENERGY_SOURCE_MANUAL:
            if current_hour in self._scheduled_hours and not self._is_paused:
                watts = float(self.config.get(CONF_MANUAL_WATT, 350))
                kwh = watts / 1000

        self._energy_today_kwh += kwh
        price = self._prices.get(current_hour, 0)
        self._cost_today += kwh * price / 100  # öre → kr

    # ------------------------------------------------------------------
    # Data for entities
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> dict[str, Any]:
        """Return current state for all entities."""
        now = dt_util.now()
        current_hour = now.hour

        # Find next scheduled start
        next_start = None
        future_hours = [h for h in self._scheduled_hours if h > current_hour]
        if future_hours:
            next_hour = min(future_hours)
            next_start = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)

        hours_remaining = len([h for h in self._scheduled_hours if h >= current_hour])

        current_price = self._prices.get(current_hour)

        kwh_per_hour = float(self.config.get(CONF_MANUAL_WATT, 350)) / 1000
        savings = get_savings(self._prices, self._scheduled_hours, kwh_per_hour)

        # Current power (from sensor or manual)
        current_power = None
        source = self.config.get(CONF_ENERGY_SOURCE)
        if source == ENERGY_SOURCE_SENSOR:
            entity_id = self.config.get(CONF_ENERGY_SENSOR)
            if entity_id:
                state = self.hass.states.get(entity_id)
                if state and state.state not in ("unavailable", "unknown"):
                    try:
                        current_power = float(state.state)
                    except ValueError:
                        pass
        elif source == ENERGY_SOURCE_MANUAL:
            if current_hour in self._scheduled_hours and not self._is_paused:
                current_power = float(self.config.get(CONF_MANUAL_WATT, 350))

        return {
            "is_active": current_hour in self._scheduled_hours and not self._is_paused,
            "is_paused": self._is_paused,
            "pause_end_time": self._pause_end_time,
            "current_price": current_price,
            "next_start": next_start,
            "hours_remaining": hours_remaining,
            "scheduled_hours": self._scheduled_hours,
            "energy_today_kwh": round(self._energy_today_kwh, 3),
            "cost_today": round(self._cost_today, 2),
            "savings_today": savings,
            "current_power": current_power,
            "pause_count_today": self._pause_count_today,
        }
