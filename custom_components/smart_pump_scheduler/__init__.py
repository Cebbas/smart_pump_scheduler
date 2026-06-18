"""Smart Pump Scheduler – Smart pump scheduler based on electricity prices."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, PLATFORMS
from .coordinator import SmartPumpSchedulerCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Pump Scheduler from a config entry."""
    config = {**entry.data, **entry.options}
    coordinator = SmartPumpSchedulerCoordinator(hass, entry.entry_id, config)

    try:
        await coordinator.async_setup()
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Failed to set up Smart Pump Scheduler: {err}") from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    _register_services(hass)

    # Listen for options updates
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Smart Pump Scheduler config entry."""
    coordinator: SmartPumpSchedulerCoordinator = hass.data[DOMAIN].get(entry.entry_id)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok and coordinator:
        await coordinator.async_teardown()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update – reload the entry."""
    await hass.config_entries.async_reload(entry.entry_id)


def _register_services(hass: HomeAssistant):
    """Register integration services."""

    async def handle_pause(call):
        minutes = call.data.get("minuter", None)
        entry_id = call.data.get("entry_id")
        coordinators = hass.data.get(DOMAIN, {})
        targets = [coordinators[entry_id]] if entry_id and entry_id in coordinators else list(coordinators.values())
        for coordinator in targets:
            await coordinator.async_pause(minutes)

    async def handle_resume(call):
        entry_id = call.data.get("entry_id")
        coordinators = hass.data.get(DOMAIN, {})
        targets = [coordinators[entry_id]] if entry_id and entry_id in coordinators else list(coordinators.values())
        for coordinator in targets:
            await coordinator.async_resume()

    async def handle_reschedule(call):
        entry_id = call.data.get("entry_id")
        coordinators = hass.data.get(DOMAIN, {})
        targets = [coordinators[entry_id]] if entry_id and entry_id in coordinators else list(coordinators.values())
        for coordinator in targets:
            await coordinator.async_force_reschedule()

    if not hass.services.has_service(DOMAIN, "pausa"):
        hass.services.async_register(DOMAIN, "pausa", handle_pause)
    if not hass.services.has_service(DOMAIN, "aterstall"):
        hass.services.async_register(DOMAIN, "aterstall", handle_resume)
    if not hass.services.has_service(DOMAIN, "uppdatera_schema"):
        hass.services.async_register(DOMAIN, "uppdatera_schema", handle_reschedule)
