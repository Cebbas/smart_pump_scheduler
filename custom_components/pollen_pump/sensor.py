"""Sensor entities for Pollen Pump."""
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
from homeassistant.const import UnitOfEnergy, UnitOfPower, CURRENCY_EURO

from .const import (
    DOMAIN,
    SUFFIX_CURRENT_PRICE,
    SUFFIX_NEXT_START,
    SUFFIX_HOURS_REMAINING,
    SUFFIX_ENERGY_TODAY,
    SUFFIX_COST_TODAY,
    SUFFIX_SAVED_TODAY,
    SUFFIX_POWER,
    CONF_NORDPOOL_CURRENCY,
)
from .coordinator import PollenPumpCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator: PollenPumpCoordinator = hass.data[DOMAIN][entry.entry_id]
    currency = entry.data.get(CONF_NORDPOOL_CURRENCY, "SEK")

    async_add_entities([
        PollenPumpPriceSensor(coordinator, entry, currency),
        PollenPumpNextStartSensor(coordinator, entry),
        PollenPumpHoursRemainingSensor(coordinator, entry),
        PollenPumpEnergyTodaySensor(coordinator, entry),
        PollenPumpCostTodaySensor(coordinator, entry, currency),
        PollenPumpSavedTodaySensor(coordinator, entry, currency),
        PollenPumpPowerSensor(coordinator, entry),
    ])


class PollenPumpPriceSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_aktuellt_pris"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry, currency):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_CURRENT_PRICE}"
        self._attr_native_unit_of_measurement = "öre/kWh" if currency in ("SEK", "NOK") else "c/kWh"

    @property
    def native_value(self):
        return self.coordinator.data.get("current_price")


class PollenPumpNextStartSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_nasta_start"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_NEXT_START}"

    @property
    def native_value(self):
        return self.coordinator.data.get("next_start")


class PollenPumpHoursRemainingSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_timmar_kvar_idag"
    _attr_native_unit_of_measurement = "h"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_HOURS_REMAINING}"

    @property
    def native_value(self):
        return self.coordinator.data.get("hours_remaining", 0)


class PollenPumpEnergyTodaySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_energi_idag"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_ENERGY_TODAY}"

    @property
    def native_value(self):
        return self.coordinator.data.get("energy_today_kwh", 0.0)


class PollenPumpCostTodaySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_kostnad_idag"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator, entry, currency):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_COST_TODAY}"
        self._attr_native_unit_of_measurement = currency

    @property
    def native_value(self):
        return self.coordinator.data.get("cost_today", 0.0)


class PollenPumpSavedTodaySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_sparade_kronor"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry, currency):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_SAVED_TODAY}"
        self._attr_native_unit_of_measurement = currency

    @property
    def native_value(self):
        return self.coordinator.data.get("savings_today", 0.0)


class PollenPumpPowerSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "pump_effekt"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SUFFIX_POWER}"

    @property
    def native_value(self):
        return self.coordinator.data.get("current_power")
