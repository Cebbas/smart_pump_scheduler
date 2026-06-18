"""Button entities – pause pump, and run it now on demand."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SUFFIX_PAUSE_BUTTON,
    SUFFIX_RUN_NOW_BUTTON,
    CONF_PAUSE_DURATION,
    CONF_RUN_NOW_DURATION,
    DEFAULT_RUN_NOW_DURATION,
)
from .coordinator import SmartPumpSchedulerCoordinator
from .device import build_device_info


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator: SmartPumpSchedulerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        SmartPumpSchedulerPauseButton(coordinator, entry),
        SmartPumpSchedulerRunNowButton(coordinator, entry),
    ])


class SmartPumpSchedulerPauseButton(CoordinatorEntity, ButtonEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_pausa"
    _attr_icon = "mdi:shower"

    def __init__(self, coordinator: SmartPumpSchedulerCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_PAUSE_BUTTON}"
        self._attr_device_info = build_device_info(entry)
        self._minutes = int(entry.data.get(CONF_PAUSE_DURATION, 60))

    async def async_press(self) -> None:
        await self.coordinator.async_pause(self._minutes)


class SmartPumpSchedulerRunNowButton(CoordinatorEntity, ButtonEntity):
    """Run the pump now for a configurable duration, e.g. right after bathing."""

    _attr_has_entity_name = True
    _attr_translation_key = "pump_kor_nu"
    _attr_icon = "mdi:play-circle"

    def __init__(self, coordinator: SmartPumpSchedulerCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_RUN_NOW_BUTTON}"
        self._attr_device_info = build_device_info(entry)

    async def async_press(self) -> None:
        minutes = int(self.coordinator.config.get(CONF_RUN_NOW_DURATION, DEFAULT_RUN_NOW_DURATION))
        await self.coordinator.async_request_run_now(minutes)
