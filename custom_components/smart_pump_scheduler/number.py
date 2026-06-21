"""Number entities – hours per day, and the run-now duration."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SUFFIX_HOURS_NUMBER,
    SUFFIX_RUN_NOW_NUMBER,
    SUFFIX_POOL_VOLUME_NUMBER,
    SUFFIX_PUMP_FLOW_NUMBER,
    CONF_HOURS_PER_DAY,
    CONF_RUN_NOW_DURATION,
    CONF_POOL_VOLUME,
    CONF_PUMP_FLOW_RATE,
    DEFAULT_HOURS_PER_DAY,
    DEFAULT_RUN_NOW_DURATION,
    DEFAULT_POOL_VOLUME,
    DEFAULT_PUMP_FLOW_RATE,
)
from .coordinator import SmartPumpSchedulerCoordinator
from .device import build_device_info


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator: SmartPumpSchedulerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        SmartPumpSchedulerHoursNumber(coordinator, entry),
        SmartPumpSchedulerRunNowMinutesNumber(coordinator, entry),
        SmartPumpSchedulerPoolVolumeNumber(coordinator, entry),
        SmartPumpSchedulerPumpFlowRateNumber(coordinator, entry),
    ])


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
        self._attr_device_info = build_device_info(entry)
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


class SmartPumpSchedulerRunNowMinutesNumber(CoordinatorEntity, NumberEntity):
    """Adjustable duration used by the "Run now" button."""

    _attr_has_entity_name = True
    _attr_translation_key = "pump_kor_nu_minuter"
    _attr_native_min_value = 5
    _attr_native_max_value = 240
    _attr_native_step = 5
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:timer-play-outline"

    def __init__(self, coordinator: SmartPumpSchedulerCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_RUN_NOW_NUMBER}"
        self._attr_device_info = build_device_info(entry)
        self._current_value = float(entry.data.get(CONF_RUN_NOW_DURATION, DEFAULT_RUN_NOW_DURATION))

    @property
    def native_value(self) -> float:
        return self._current_value

    async def async_set_native_value(self, value: float) -> None:
        self._current_value = value
        self.coordinator.config[CONF_RUN_NOW_DURATION] = int(value)
        self.async_write_ha_state()


class SmartPumpSchedulerPoolVolumeNumber(CoordinatorEntity, NumberEntity):
    """Pool volume, used to calculate a recommended daily pump runtime."""

    _attr_has_entity_name = True
    _attr_translation_key = "pump_poolvolym"
    _attr_native_min_value = 0
    _attr_native_max_value = 500
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = "m³"
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:pool"

    def __init__(self, coordinator: SmartPumpSchedulerCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_POOL_VOLUME_NUMBER}"
        self._attr_device_info = build_device_info(entry)
        self._current_value = float(entry.data.get(CONF_POOL_VOLUME, DEFAULT_POOL_VOLUME))

    @property
    def native_value(self) -> float:
        return self._current_value

    async def async_set_native_value(self, value: float) -> None:
        self._current_value = value
        self.coordinator.config[CONF_POOL_VOLUME] = value
        await self.coordinator.async_refresh()
        self.async_write_ha_state()


class SmartPumpSchedulerPumpFlowRateNumber(CoordinatorEntity, NumberEntity):
    """Pump flow rate, used to calculate a recommended daily pump runtime."""

    _attr_has_entity_name = True
    _attr_translation_key = "pump_pumpflode"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 0.1
    _attr_native_unit_of_measurement = "m³/h"
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:pump"

    def __init__(self, coordinator: SmartPumpSchedulerCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_PUMP_FLOW_NUMBER}"
        self._attr_device_info = build_device_info(entry)
        self._current_value = float(entry.data.get(CONF_PUMP_FLOW_RATE, DEFAULT_PUMP_FLOW_RATE))

    @property
    def native_value(self) -> float:
        return self._current_value

    async def async_set_native_value(self, value: float) -> None:
        self._current_value = value
        self.coordinator.config[CONF_PUMP_FLOW_RATE] = value
        await self.coordinator.async_refresh()
        self.async_write_ha_state()
