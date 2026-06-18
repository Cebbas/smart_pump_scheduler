"""Binary sensor – pump schema active or not."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SUFFIX_SCHEMA
from .coordinator import SmartPumpSchedulerCoordinator
from .device import build_device_info


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator: SmartPumpSchedulerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SmartPumpSchedulerSchemaSensor(coordinator, entry)])


class SmartPumpSchedulerSchemaSensor(CoordinatorEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_has_entity_name = True
    _attr_translation_key = "pump_schema"

    def __init__(self, coordinator: SmartPumpSchedulerCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_SCHEMA}"
        self._attr_device_info = build_device_info(entry)

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("is_active", False)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        return {
            "scheduled_hours": data.get("scheduled_hours", []),
            "is_paused": data.get("is_paused", False),
            "pause_end_time": str(data.get("pause_end_time")) if data.get("pause_end_time") else None,
            "pause_count_today": data.get("pause_count_today", 0),
            "run_now_active": data.get("run_now_active", False),
            "run_now_until": str(data.get("run_now_until")) if data.get("run_now_until") else None,
            "run_now_pending": data.get("run_now_pending", False),
        }
