"""Shared device info so all entities group under one device card."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, VERSION


def build_device_info(entry: ConfigEntry) -> DeviceInfo:
    """Return the DeviceInfo shared by every entity of a config entry."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title or "Smart Pump Scheduler",
        manufacturer="Smart Pump Scheduler",
        model="Price-based pump scheduler",
        sw_version=VERSION,
        configuration_url="https://github.com/Cebbas/smart_pump_scheduler",
    )
