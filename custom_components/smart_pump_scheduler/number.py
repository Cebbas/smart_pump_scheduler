"""Number entity – hours per day."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SUFFIX_HOURS_NUMBER, CONF_HOURS_PER_DAY, DEFAULT_HOURS_PER_DAY
from .coordinator import SmartPumpSchedulerCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator: SmartPumpSchedulerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SmartPumpSchedulerHoursNumber(coordinator, entry)])


class SmartPumpSchedulerHoursNumber(CoordinatorEntity, NumberEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_timmar_per_dygn"
    _attr_native_min_value = 1
    _attr_native_max_value = 24
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:clock-outline"

    def __init__(self, coordinator: SmartPumpSchedulerCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_HOURS_NUMBER}"
        self._current_value = float(entry.data.get(CONF_HOURS_PER_DAY, DEFAULT_HOURS_PER_DAY))

    @property
    def native_value(self) -> float:
        return self._current_value

    async def async_set_native_value(self, value: float) -> None:
        self._current_value = value
        self.coordinator.config[CONF_HOURS_PER_DAY] = int(value)
        # Trigger a reschedule with new hours
        await self.coordinator.async_force_reschedule()
        self.async_write_ha_state()
