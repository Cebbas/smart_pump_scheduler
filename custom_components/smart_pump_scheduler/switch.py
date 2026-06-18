"""Switch entity – pause/resume toggle."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SUFFIX_PAUSE_SWITCH
from .coordinator import SmartPumpSchedulerCoordinator
from .device import build_device_info


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator: SmartPumpSchedulerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SmartPumpSchedulerPauseSwitch(coordinator, entry)])


class SmartPumpSchedulerPauseSwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_paus"
    _attr_icon = "mdi:pause-circle"

    def __init__(self, coordinator: SmartPumpSchedulerCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_PAUSE_SWITCH}"
        self._attr_device_info = build_device_info(entry)

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("is_paused", False)

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_pause()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_resume()
