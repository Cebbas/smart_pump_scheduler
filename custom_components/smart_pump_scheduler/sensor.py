"""Sensor entities for Smart Pump Scheduler."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfEnergy, UnitOfPower, UnitOfTime, CURRENCY_EURO

from .const import (
    DOMAIN,
    SUFFIX_CURRENT_PRICE,
    SUFFIX_NEXT_START,
    SUFFIX_HOURS_REMAINING,
    SUFFIX_SCHEDULED_HOURS,
    SUFFIX_ENERGY_TODAY,
    SUFFIX_RUNTIME_TODAY,
    SUFFIX_COST_TODAY,
    SUFFIX_SAVED_TODAY,
    SUFFIX_POWER,
    SUFFIX_RECOMMENDED_HOURS,
    SUFFIX_STATUS,
    STATUS_RUNNING_SCHEDULED,
    STATUS_RUNNING_MANUAL,
    STATUS_PAUSED,
    STATUS_WAITING_RUN_NOW,
    STATUS_IDLE,
    CONF_NORDPOOL_CURRENCY,
)
from .coordinator import SmartPumpSchedulerCoordinator
from .device import build_device_info
from .scheduler import format_hour_ranges, format_duration_hm


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator: SmartPumpSchedulerCoordinator = hass.data[DOMAIN][entry.entry_id]
    currency = entry.data.get(CONF_NORDPOOL_CURRENCY, "SEK")

    async_add_entities([
        SmartPumpSchedulerPriceSensor(coordinator, entry, currency),
        SmartPumpSchedulerNextStartSensor(coordinator, entry),
        SmartPumpSchedulerHoursRemainingSensor(coordinator, entry),
        SmartPumpSchedulerScheduledHoursSensor(coordinator, entry),
        SmartPumpSchedulerEnergyTodaySensor(coordinator, entry),
        SmartPumpSchedulerRuntimeTodaySensor(coordinator, entry),
        SmartPumpSchedulerCostTodaySensor(coordinator, entry, currency),
        SmartPumpSchedulerSavedTodaySensor(coordinator, entry, currency),
        SmartPumpSchedulerPowerSensor(coordinator, entry),
        SmartPumpSchedulerRecommendedHoursSensor(coordinator, entry),
        SmartPumpSchedulerStatusSensor(coordinator, entry),
    ])


class SmartPumpSchedulerPriceSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_aktuellt_pris"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry, currency):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_CURRENT_PRICE}"
        self._attr_device_info = build_device_info(entry)
        self._attr_native_unit_of_measurement = "öre/kWh" if currency in ("SEK", "NOK") else "c/kWh"

    @property
    def native_value(self):
        return self.coordinator.data.get("current_price")


class SmartPumpSchedulerNextStartSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_nasta_start"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_NEXT_START}"
        self._attr_device_info = build_device_info(entry)

    @property
    def native_value(self):
        return self.coordinator.data.get("next_start")


class SmartPumpSchedulerHoursRemainingSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_timmar_kvar_idag"
    _attr_native_unit_of_measurement = "h"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_HOURS_REMAINING}"
        self._attr_device_info = build_device_info(entry)

    @property
    def native_value(self):
        return self.coordinator.data.get("hours_remaining", 0)


class SmartPumpSchedulerScheduledHoursSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_schemalagda_timmar"
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_SCHEDULED_HOURS}"
        self._attr_device_info = build_device_info(entry)

    @property
    def native_value(self):
        return format_hour_ranges(self.coordinator.data.get("scheduled_hours", []))

    @property
    def extra_state_attributes(self):
        return {
            "hours": self.coordinator.data.get("scheduled_hours", []),
            "prices": self.coordinator.data.get("prices", {}),
        }


class SmartPumpSchedulerEnergyTodaySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_energi_idag"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_ENERGY_TODAY}"
        self._attr_device_info = build_device_info(entry)

    @property
    def native_value(self):
        return self.coordinator.data.get("energy_today_kwh", 0.0)


class SmartPumpSchedulerRuntimeTodaySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_drifttid_idag"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_RUNTIME_TODAY}"
        self._attr_device_info = build_device_info(entry)

    @property
    def native_value(self):
        return self.coordinator.data.get("runtime_today_minutes", 0.0)

    @property
    def extra_state_attributes(self):
        return {"formatted": format_duration_hm(self.coordinator.data.get("runtime_today_minutes", 0.0))}


class SmartPumpSchedulerCostTodaySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_kostnad_idag"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator, entry, currency):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_COST_TODAY}"
        self._attr_device_info = build_device_info(entry)
        self._attr_native_unit_of_measurement = currency

    @property
    def native_value(self):
        return self.coordinator.data.get("cost_today", 0.0)


class SmartPumpSchedulerSavedTodaySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_sparade_kronor"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry, currency):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_SAVED_TODAY}"
        self._attr_device_info = build_device_info(entry)
        self._attr_native_unit_of_measurement = currency

    @property
    def native_value(self):
        return self.coordinator.data.get("savings_today", 0.0)


class SmartPumpSchedulerPowerSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_effekt"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_POWER}"
        self._attr_device_info = build_device_info(entry)

    @property
    def native_value(self):
        return self.coordinator.data.get("current_power")


class SmartPumpSchedulerRecommendedHoursSensor(CoordinatorEntity, SensorEntity):
    """Recommended daily runtime so the pool volume is fully circulated once."""

    _attr_has_entity_name = True
    _attr_translation_key = "pump_rekommenderade_timmar"
    _attr_native_unit_of_measurement = "h"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:pool"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_RECOMMENDED_HOURS}"
        self._attr_device_info = build_device_info(entry)

    @property
    def native_value(self):
        return self.coordinator.data.get("recommended_hours")


class SmartPumpSchedulerStatusSensor(CoordinatorEntity, SensorEntity):
    """What the pump is doing right now, in priority order."""

    _attr_has_entity_name = True
    _attr_translation_key = "pump_status"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [
        STATUS_RUNNING_MANUAL,
        STATUS_RUNNING_SCHEDULED,
        STATUS_WAITING_RUN_NOW,
        STATUS_PAUSED,
        STATUS_IDLE,
    ]
    _attr_icon = "mdi:water-pump"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_STATUS}"
        self._attr_device_info = build_device_info(entry)

    @property
    def native_value(self):
        data = self.coordinator.data
        if data.get("run_now_active"):
            return STATUS_RUNNING_MANUAL
        if data.get("is_paused"):
            return STATUS_PAUSED
        if data.get("run_now_pending"):
            return STATUS_WAITING_RUN_NOW
        if data.get("is_active"):
            return STATUS_RUNNING_SCHEDULED
        return STATUS_IDLE
