"""Scheduling algorithm for Smart Pump Scheduler."""
from __future__ import annotations

import logging
from datetime import datetime, time
from typing import Optional

from .const import (
    WEEKDAYS,
    WEEKDAY_LABELS,
    CONF_HOURS_PER_DAY,
    CONF_MIN_PRICE,
    CONF_MAX_PRICE,
    CONF_PER_WEEKDAY,
    CONF_GLOBAL_START,
    CONF_GLOBAL_STOP,
    DEFAULT_HOURS_PER_DAY,
    DEFAULT_GLOBAL_START,
    DEFAULT_GLOBAL_STOP,
)

_LOGGER = logging.getLogger(__name__)


def build_schedule(
    prices: dict[int, float],
    config: dict,
    paused_hours: set[int] | None = None,
    extra_hours_needed: int = 0,
    now: datetime | None = None,
) -> list[int]:
    """
    Calculate which hours the pump should run today.

    Args:
        prices: {hour(0-23): price}
        config: integration config dict
        paused_hours: hours that were paused and should not count
        extra_hours_needed: additional hours to schedule (from pauses)
        now: current datetime (used to skip past hours on recalculation)

    Returns:
        Sorted list of hours when pump should run.
    """
    if now is None:
        now = datetime.now()

    paused_hours = paused_hours or set()
    weekday_name = WEEKDAYS[now.weekday()]

    # Check if this day is active
    if not config.get(f"{weekday_name}_active", True):
        _LOGGER.debug("Pump disabled for %s", weekday_name)
        return []

    # Get time window for today
    start_time, stop_time = _get_time_window(config, weekday_name)
    start_hour = start_time.hour
    stop_hour = stop_time.hour if stop_time != time(0, 0) else 24

    # Get hours per day for today
    hours_needed = _get_hours_for_day(config, weekday_name) + extra_hours_needed

    # Filter to hours within time window
    available_hours = {
        h: p for h, p in prices.items()
        if start_hour <= h < stop_hour
    }

    if not available_hours:
        _LOGGER.warning("No prices available within time window %s-%s", start_hour, stop_hour)
        return []

    min_price = config.get(CONF_MIN_PRICE)
    max_price = config.get(CONF_MAX_PRICE)

    # Always-run hours (price below minimum threshold)
    always_run = set()
    if min_price is not None:
        always_run = {h for h, p in available_hours.items() if p <= min_price}

    # Never-run hours (price above maximum threshold)
    never_run = set()
    if max_price is not None:
        never_run = {h for h, p in available_hours.items() if p > max_price}

    # Remove never-run and always-run from the pool to sort
    pool = {
        h: p for h, p in available_hours.items()
        if h not in always_run and h not in never_run and h not in paused_hours
    }

    # Sort pool cheapest first
    sorted_hours = sorted(pool.keys(), key=lambda h: pool[h])

    # How many more hours do we need beyond always_run?
    already_scheduled = len(always_run - never_run - paused_hours)
    remaining_needed = max(0, hours_needed - already_scheduled)

    # Pick cheapest hours from pool
    chosen = sorted_hours[:remaining_needed]

    # Combine
    final_hours = sorted(
        (always_run | set(chosen)) - never_run - paused_hours
    )

    # Warn if we couldn't fit all hours
    if len(final_hours) < hours_needed - len(paused_hours):
        _LOGGER.warning(
            "Could only schedule %d of %d requested hours within window",
            len(final_hours),
            hours_needed,
        )

    _LOGGER.debug(
        "Scheduled hours for %s: %s (window %s-%s, needed %d)",
        weekday_name,
        final_hours,
        start_hour,
        stop_hour,
        hours_needed,
    )

    return final_hours


def find_next_available_hour(
    prices: dict[int, float],
    scheduled_hours: list[int],
    paused_hour: int,
    config: dict,
    now: datetime | None = None,
) -> int | None:
    """
    After a pause, find the next cheapest unscheduled hour to compensate.

    Returns the hour to add, or None if no hour is available.
    """
    if now is None:
        now = datetime.now()

    weekday_name = WEEKDAYS[now.weekday()]
    start_time, stop_time = _get_time_window(config, weekday_name)
    start_hour = start_time.hour
    stop_hour = stop_time.hour if stop_time != time(0, 0) else 24
    current_hour = now.hour

    max_price = config.get(CONF_MAX_PRICE)
    scheduled_set = set(scheduled_hours)

    # Candidate hours: in window, not yet passed, not already scheduled, not the paused hour
    candidates = {
        h: p for h, p in prices.items()
        if start_hour <= h < stop_hour
        and h > current_hour  # must be in the future
        and h not in scheduled_set
        and h != paused_hour
        and (max_price is None or p <= max_price)
    }

    if not candidates:
        _LOGGER.info("No available hours to compensate for pause")
        return None

    # Pick cheapest candidate
    return min(candidates.keys(), key=lambda h: candidates[h])


def get_savings(
    prices: dict[int, float],
    scheduled_hours: list[int],
    kwh_per_hour: float,
) -> float:
    """
    Calculate savings vs running during the N most expensive hours.
    Returns savings in same currency unit as prices.
    """
    if not scheduled_hours or not prices:
        return 0.0

    n = len(scheduled_hours)
    all_hours_sorted_expensive = sorted(prices.keys(), key=lambda h: prices[h], reverse=True)
    expensive_hours = all_hours_sorted_expensive[:n]

    cost_expensive = sum(prices.get(h, 0) * kwh_per_hour for h in expensive_hours)
    cost_actual = sum(prices.get(h, 0) * kwh_per_hour for h in scheduled_hours)

    return round(max(0.0, cost_expensive - cost_actual), 2)


def _get_time_window(config: dict, weekday_name: str) -> tuple[time, time]:
    """Get start/stop time for a given weekday."""
    per_weekday = config.get(CONF_PER_WEEKDAY, False)

    if per_weekday:
        start_str = config.get(f"{weekday_name}_start", DEFAULT_GLOBAL_START)
        stop_str = config.get(f"{weekday_name}_stop", DEFAULT_GLOBAL_STOP)
    else:
        start_str = config.get(CONF_GLOBAL_START, DEFAULT_GLOBAL_START)
        stop_str = config.get(CONF_GLOBAL_STOP, DEFAULT_GLOBAL_STOP)

    return _parse_time(start_str), _parse_time(stop_str)


def _get_hours_for_day(config: dict, weekday_name: str) -> int:
    """Get number of hours to run for a given weekday."""
    per_weekday = config.get(CONF_PER_WEEKDAY, False)
    if per_weekday:
        day_hours = config.get(f"{weekday_name}_hours")
        if day_hours is not None:
            return int(day_hours)
    return int(config.get(CONF_HOURS_PER_DAY, DEFAULT_HOURS_PER_DAY))


def _parse_time(time_str: str) -> time:
    """Parse HH:MM string to time object. 24:00 becomes 00:00."""
    if time_str == "24:00":
        return time(0, 0)
    try:
        parts = time_str.split(":")
        return time(int(parts[0]), int(parts[1]))
    except Exception:
        return time(0, 0)
