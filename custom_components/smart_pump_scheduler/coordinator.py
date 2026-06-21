"""Coordinator for Smart Pump Scheduler – manages prices, schedule and pause state."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import (
    async_track_time_change,
    async_call_later,
    async_track_state_change_event,
)
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
    CONF_MAX_PRICE,
    CONF_RUN_NOW_DURATION,
    CONF_NORDPOOL_AREA,
    CONF_NORDPOOL_CURRENCY,
    CONF_NORDPOOL_VAT,
    CONF_ENABLE_POOL_RECOMMENDATION,
    CONF_POOL_VOLUME,
    CONF_PUMP_FLOW_RATE,
    PRICE_SOURCE_NORDPOOL,
    PRICE_SOURCE_SENSOR,
    ENERGY_SOURCE_SENSOR,
    ENERGY_SOURCE_MANUAL,
    COORDINATOR_UPDATE_INTERVAL,
    PRICE_RETRY_INTERVAL,
    DEFAULT_RUN_NOW_DURATION,
)
from .price_fetcher import fetch_nordpool_prices, get_hourly_prices_from_sensor
from .scheduler import build_schedule, find_next_available_hour, get_savings, calculate_recommended_hours

_LOGGER = logging.getLogger(__name__)


class SmartPumpSchedulerCoordinator(DataUpdateCoordinator):
    """Manages all state for one Smart Pump Scheduler instance."""

    def __init__(self, hass: HomeAssistant, entry_id: str, config: dict):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=COORDINATOR_UPDATE_INTERVAL),
        )
        self.entry_id = entry_id
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
        self._runtime_today_seconds: float = 0.0
        self._runtime_segment_start: datetime | None = None
        self._run_now_until: datetime | None = None
        self._run_now_pending_minutes: int | None = None
        self._session: aiohttp.ClientSession | None = None
        self._unsub_midnight = None
        self._unsub_hourly = None
        self._unsub_switch = None

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
        # Track the pump switch's actual on/off state to measure real runtime
        switch_entity = self.config.get(CONF_SWITCH_ENTITY)
        if switch_entity:
            self._unsub_switch = async_track_state_change_event(
                self.hass, [switch_entity], self._handle_switch_state_change
            )
            state = self.hass.states.get(switch_entity)
            if state and state.state == "on":
                self._runtime_segment_start = dt_util.now()
        # Initial fetch
        await self._fetch_prices_and_build_schedule()

    async def async_teardown(self):
        """Remove listeners on unload."""
        if self._unsub_midnight:
            self._unsub_midnight()
        if self._unsub_hourly:
            self._unsub_hourly()
        if self._unsub_switch:
            self._unsub_switch()
        if self._session and not self._session.closed:
            await self._session.close()
        ir.async_delete_issue(self.hass, DOMAIN, f"schedule_shortfall_{self.entry_id}")
        ir.async_delete_issue(self.hass, DOMAIN, f"run_now_waiting_{self.entry_id}")

    # ------------------------------------------------------------------
    # Actual runtime tracking
    # ------------------------------------------------------------------

    @callback
    def _handle_switch_state_change(self, event):
        """Track real on/off transitions of the pump switch to measure runtime."""
        new_state = event.data.get("new_state")
        old_state = event.data.get("old_state")
        now = dt_util.now()

        was_on = old_state is not None and old_state.state == "on"
        is_on = new_state is not None and new_state.state == "on"

        if is_on and not was_on:
            self._runtime_segment_start = now
        elif was_on and not is_on and self._runtime_segment_start is not None:
            self._runtime_today_seconds += (now - self._runtime_segment_start).total_seconds()
            self._runtime_segment_start = None

        self.hass.async_create_task(self.async_refresh())

    def _runtime_today_minutes(self, now: datetime) -> float:
        """Today's accumulated runtime in minutes, including any open segment."""
        seconds = self._runtime_today_seconds
        if self._runtime_segment_start is not None:
            seconds += (now - self._runtime_segment_start).total_seconds()
        return round(seconds / 60, 1)

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
        result = build_schedule(
            prices=prices,
            config=self.config,
            paused_hours=self._paused_hours,
        )
        self._scheduled_hours = result.hours
        self._update_shortfall_issue(result)
        await self._apply_schedule()
        await self.async_refresh()

    def _update_shortfall_issue(self, result) -> None:
        """Raise or clear a Repairs issue if not all requested hours fit."""
        issue_id = f"schedule_shortfall_{self.entry_id}"
        if result.shortfall > 0:
            ir.async_create_issue(
                self.hass,
                DOMAIN,
                issue_id,
                is_fixable=False,
                severity=ir.IssueSeverity.WARNING,
                translation_key="schedule_shortfall",
                translation_placeholders={
                    "scheduled": str(len(result.hours)),
                    "needed": str(result.hours_needed),
                },
            )
        else:
            ir.async_delete_issue(self.hass, DOMAIN, issue_id)

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

        run_now_active = self._run_now_until is not None and now < self._run_now_until
        should_run = (
            current_hour in self._scheduled_hours
            and not self._is_paused
        ) or run_now_active

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

        # Start today's count fresh; if the pump is still running across
        # midnight, keep the segment open from this moment rather than
        # carrying yesterday's elapsed time into today's total.
        self._runtime_today_seconds = 0.0
        if self._runtime_segment_start is not None:
            self._runtime_segment_start = now

        # A "run now" request is a same-day ask; don't carry it into a new day.
        if self._run_now_pending_minutes is not None:
            _LOGGER.info("Clearing unfulfilled run-now request at day rollover")
            self._run_now_pending_minutes = None
            self._update_run_now_issue()

        self.hass.async_create_task(self._fetch_prices_and_build_schedule())

    @callback
    def _handle_hourly(self, now: datetime):
        """Called every hour – apply schedule and track energy."""
        self.hass.async_create_task(self._apply_schedule())
        self.hass.async_create_task(self._update_energy())
        self.hass.async_create_task(self._check_pending_run_now())
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

        # Pausing always wins over an active or queued run-now request.
        self._run_now_until = None
        if self._run_now_pending_minutes is not None:
            self._run_now_pending_minutes = None
            self._update_run_now_issue()

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

        # Only add a compensation hour if the pump was actually scheduled
        # to run during the paused hour – pausing during an "off" hour
        # shouldn't grant an extra hour elsewhere.
        was_scheduled = current_hour in self._scheduled_hours
        if current_hour in self._scheduled_hours:
            self._scheduled_hours.remove(current_hour)

        if was_scheduled:
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
        else:
            _LOGGER.debug("Pump wasn't scheduled during hour %d, no compensation needed", current_hour)

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
    # Run now (manual on-demand run, e.g. after bathing)
    # ------------------------------------------------------------------

    async def async_request_run_now(self, minutes: int | None = None) -> bool:
        """
        Request running the pump for `minutes` right away.

        If the current price is above the configured max price, the
        request is queued instead and fulfilled as soon as an hour with
        an acceptable price comes up (checked hourly).

        Returns True if the pump started running immediately, False if
        the request was queued.
        """
        if minutes is None:
            minutes = int(self.config.get(CONF_RUN_NOW_DURATION, DEFAULT_RUN_NOW_DURATION))

        if self._price_ok_for_run_now():
            await self._start_run_now(minutes)
            return True

        self._run_now_pending_minutes = minutes
        self._update_run_now_issue()
        _LOGGER.info("Run-now requested but price is above the max threshold; waiting")
        await self.async_refresh()
        return False

    def _price_ok_for_run_now(self) -> bool:
        max_price = self.config.get(CONF_MAX_PRICE)
        if max_price is None:
            return True
        current_price = self._prices.get(dt_util.now().hour)
        return current_price is None or current_price <= max_price

    async def _start_run_now(self, minutes: int):
        """Turn the pump on now for `minutes`, overriding the schedule."""
        was_queued = self._run_now_pending_minutes is not None

        now = dt_util.now()
        self._run_now_until = now + timedelta(minutes=minutes)
        self._run_now_pending_minutes = None
        self._update_run_now_issue()
        await self._apply_schedule()
        async_call_later(
            self.hass,
            minutes * 60,
            lambda _: self.hass.async_create_task(self._end_run_now()),
        )

        if was_queued:
            await self._notify_run_now_started(minutes)

        await self.async_refresh()

    async def _notify_run_now_started(self, minutes: int) -> None:
        """Notify the user that a deferred run-now request has started."""
        current_price = self._prices.get(dt_util.now().hour)
        price_text = f" ({current_price})" if current_price is not None else ""
        await self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Smart Pump Scheduler",
                "message": f"Price dropped below the max threshold{price_text} – the pump is now running for {minutes} minutes.",
                "notification_id": f"smart_pump_scheduler_run_now_{self.entry_id}",
            },
            blocking=False,
        )

    async def _end_run_now(self):
        """Hand control back to the normal schedule after a run-now session."""
        self._run_now_until = None
        await self._apply_schedule()
        await self.async_refresh()

    async def _check_pending_run_now(self):
        """Called hourly: start a queued run-now request once the price allows it."""
        if self._run_now_pending_minutes is not None and self._price_ok_for_run_now():
            minutes = self._run_now_pending_minutes
            await self._start_run_now(minutes)

    def _update_run_now_issue(self) -> None:
        """Raise or clear a Repairs issue while a run-now request is queued."""
        issue_id = f"run_now_waiting_{self.entry_id}"
        if self._run_now_pending_minutes is not None:
            max_price = self.config.get(CONF_MAX_PRICE)
            current_price = self._prices.get(dt_util.now().hour)
            ir.async_create_issue(
                self.hass,
                DOMAIN,
                issue_id,
                is_fixable=False,
                severity=ir.IssueSeverity.WARNING,
                translation_key="run_now_waiting",
                translation_placeholders={
                    "current_price": str(current_price) if current_price is not None else "?",
                    "max_price": str(max_price),
                },
            )
        else:
            ir.async_delete_issue(self.hass, DOMAIN, issue_id)

    def as_diagnostics(self) -> dict[str, Any]:
        """Return internal state for the diagnostics platform."""
        return {
            "prices": self._prices,
            "scheduled_hours": self._scheduled_hours,
            "paused_hours": sorted(self._paused_hours),
            "pause_count_today": self._pause_count_today,
            "is_paused": self._is_paused,
            "pause_end_time": str(self._pause_end_time) if self._pause_end_time else None,
            "run_now_active": self._run_now_until is not None,
            "run_now_until": str(self._run_now_until) if self._run_now_until else None,
            "run_now_pending_minutes": self._run_now_pending_minutes,
            "energy_today_kwh": self._energy_today_kwh,
            "runtime_today_minutes": self._runtime_today_minutes(dt_util.now()),
            "cost_today": self._cost_today,
        }

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

        recommended_hours = None
        if self.config.get(CONF_ENABLE_POOL_RECOMMENDATION, False):
            recommended_hours = calculate_recommended_hours(
                self.config.get(CONF_POOL_VOLUME, 0),
                self.config.get(CONF_PUMP_FLOW_RATE, 0),
            )

        run_now_active = self._run_now_until is not None and now < self._run_now_until
        return {
            "is_active": (current_hour in self._scheduled_hours and not self._is_paused) or run_now_active,
            "is_paused": self._is_paused,
            "pause_end_time": self._pause_end_time,
            "run_now_active": run_now_active,
            "run_now_until": self._run_now_until,
            "run_now_pending": self._run_now_pending_minutes is not None,
            "current_price": current_price,
            "next_start": next_start,
            "hours_remaining": hours_remaining,
            "scheduled_hours": self._scheduled_hours,
            "prices": self._prices,
            "energy_today_kwh": round(self._energy_today_kwh, 3),
            "runtime_today_minutes": self._runtime_today_minutes(now),
            "cost_today": round(self._cost_today, 2),
            "savings_today": savings,
            "current_power": current_power,
            "pause_count_today": self._pause_count_today,
            "recommended_hours": recommended_hours,
        }
