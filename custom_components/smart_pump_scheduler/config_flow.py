"""Config flow for Smart Pump Scheduler integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_PRICE_SOURCE,
    CONF_NORDPOOL_AREA,
    CONF_NORDPOOL_CURRENCY,
    CONF_NORDPOOL_VAT,
    CONF_PRICE_SENSOR,
    CONF_SWITCH_ENTITY,
    CONF_HOURS_PER_DAY,
    CONF_MIN_PRICE,
    CONF_MAX_PRICE,
    CONF_PER_WEEKDAY,
    CONF_GLOBAL_START,
    CONF_GLOBAL_STOP,
    CONF_WEEKDAY_SCHEDULE,
    CONF_ENABLE_PAUSE,
    CONF_PAUSE_DURATION,
    CONF_MAX_PAUSES,
    CONF_ENERGY_SOURCE,
    CONF_ENERGY_SENSOR,
    CONF_MANUAL_WATT,
    PRICE_SOURCE_NORDPOOL,
    PRICE_SOURCE_SENSOR,
    PRICE_SOURCE_FIXED,
    ENERGY_SOURCE_SENSOR,
    ENERGY_SOURCE_MANUAL,
    ENERGY_SOURCE_NONE,
    NORDPOOL_AREAS,
    NORDPOOL_CURRENCIES,
    WEEKDAYS,
    DEFAULT_HOURS_PER_DAY,
    DEFAULT_PAUSE_DURATION,
    DEFAULT_MAX_PAUSES,
    DEFAULT_GLOBAL_START,
    DEFAULT_GLOBAL_STOP,
    DEFAULT_MANUAL_WATT,
)


class SmartPumpSchedulerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Smart Pump Scheduler."""

    VERSION = 1

    def __init__(self):
        self._data = {}

    async def async_step_user(self, user_input=None):
        """Step 1: Choose price source."""
        if user_input is not None:
            self._data.update(user_input)
            source = user_input[CONF_PRICE_SOURCE]
            if source == PRICE_SOURCE_NORDPOOL:
                return await self.async_step_nordpool()
            elif source == PRICE_SOURCE_SENSOR:
                return await self.async_step_price_sensor()
            else:
                return await self.async_step_pump_settings()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME, default="Pump"): selector.TextSelector(),
                vol.Required(CONF_PRICE_SOURCE, default=PRICE_SOURCE_NORDPOOL): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": PRICE_SOURCE_NORDPOOL, "label": "Nordpool"},
                            {"value": PRICE_SOURCE_SENSOR, "label": "HA Sensor"},
                            {"value": PRICE_SOURCE_FIXED, "label": "Fixed schedule"},
                        ],
                        mode=selector.SelectSelectorMode.LIST,
                        translation_key="price_source",
                    )
                ),
            }),
        )

    async def async_step_nordpool(self, user_input=None):
        """Step 2a: Nordpool settings."""
        errors = {}
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_pump_settings()

        return self.async_show_form(
            step_id="nordpool",
            data_schema=vol.Schema({
                vol.Required(CONF_NORDPOOL_AREA, default="SE3"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=NORDPOOL_AREAS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(CONF_NORDPOOL_CURRENCY, default="SEK"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=NORDPOOL_CURRENCIES,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(CONF_NORDPOOL_VAT, default=True): selector.BooleanSelector(),
            }),
            errors=errors,
        )

    async def async_step_price_sensor(self, user_input=None):
        """Step 2b: Choose existing HA sensor."""
        errors = {}
        if user_input is not None:
            entity_id = user_input[CONF_PRICE_SENSOR]
            state = self.hass.states.get(entity_id)
            if state is None:
                errors[CONF_PRICE_SENSOR] = "invalid_sensor"
            else:
                self._data.update(user_input)
                return await self.async_step_pump_settings()

        return self.async_show_form(
            step_id="price_sensor",
            data_schema=vol.Schema({
                vol.Required(CONF_PRICE_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
            }),
            errors=errors,
        )

    async def async_step_pump_settings(self, user_input=None):
        """Step 3: Pump settings."""
        errors = {}
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_schedule()

        return self.async_show_form(
            step_id="pump_settings",
            data_schema=vol.Schema({
                vol.Required(CONF_SWITCH_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="switch")
                ),
                vol.Required(CONF_HOURS_PER_DAY, default=DEFAULT_HOURS_PER_DAY): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=1, max=24, step=1, mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Optional(CONF_MIN_PRICE): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=500, step=1, mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Optional(CONF_MAX_PRICE): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=500, step=1, mode=selector.NumberSelectorMode.BOX)
                ),
            }),
            errors=errors,
        )

    async def async_step_schedule(self, user_input=None):
        """Step 4: Time schedule per weekday."""
        errors = {}
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_pause()

        schema_dict = {
            vol.Required(CONF_PER_WEEKDAY, default=False): selector.BooleanSelector(),
            vol.Required(CONF_GLOBAL_START, default=DEFAULT_GLOBAL_START): selector.TimeSelector(),
            vol.Required(CONF_GLOBAL_STOP, default=DEFAULT_GLOBAL_STOP): selector.TimeSelector(),
        }

        for day in WEEKDAYS:
            schema_dict[vol.Optional(f"{day}_active", default=True)] = selector.BooleanSelector()
            schema_dict[vol.Optional(f"{day}_start", default="06:00")] = selector.TimeSelector()
            schema_dict[vol.Optional(f"{day}_stop", default="22:00")] = selector.TimeSelector()
            schema_dict[vol.Optional(f"{day}_hours", default=DEFAULT_HOURS_PER_DAY)] = selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, max=24, step=1, mode=selector.NumberSelectorMode.BOX)
            )

        return self.async_show_form(
            step_id="schedule",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
        )

    async def async_step_pause(self, user_input=None):
        """Step 5: Pause settings."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_energy()

        return self.async_show_form(
            step_id="pause",
            data_schema=vol.Schema({
                vol.Required(CONF_ENABLE_PAUSE, default=True): selector.BooleanSelector(),
                vol.Required(CONF_PAUSE_DURATION, default=DEFAULT_PAUSE_DURATION): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=5, max=480, step=5, mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Required(CONF_MAX_PAUSES, default=DEFAULT_MAX_PAUSES): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=1, max=20, step=1, mode=selector.NumberSelectorMode.BOX)
                ),
            }),
        )

    async def async_step_energy(self, user_input=None):
        """Step 6: Energy monitoring."""
        errors = {}
        if user_input is not None:
            source = user_input.get(CONF_ENERGY_SOURCE)
            if source == ENERGY_SOURCE_MANUAL:
                watt = user_input.get(CONF_MANUAL_WATT, 0)
                if watt < 1:
                    errors[CONF_MANUAL_WATT] = "invalid_watt"
            if source == ENERGY_SOURCE_SENSOR:
                entity_id = user_input.get(CONF_ENERGY_SENSOR)
                if entity_id and self.hass.states.get(entity_id) is None:
                    errors[CONF_ENERGY_SENSOR] = "invalid_sensor"
            if not errors:
                self._data.update(user_input)
                return self.async_create_entry(
                    title=self._data.get(CONF_NAME, "Smart Pump Scheduler"),
                    data=self._data,
                )

        return self.async_show_form(
            step_id="energy",
            data_schema=vol.Schema({
                vol.Required(CONF_ENERGY_SOURCE, default=ENERGY_SOURCE_NONE): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": ENERGY_SOURCE_SENSOR, "label": "Energy sensor"},
                            {"value": ENERGY_SOURCE_MANUAL, "label": "Manual watt"},
                            {"value": ENERGY_SOURCE_NONE, "label": "None"},
                        ],
                        mode=selector.SelectSelectorMode.LIST,
                        translation_key="energy_source",
                    )
                ),
                vol.Optional(CONF_ENERGY_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Optional(CONF_MANUAL_WATT, default=DEFAULT_MANUAL_WATT): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=1, max=100000, step=1, mode=selector.NumberSelectorMode.BOX)
                ),
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SmartPumpSchedulerOptionsFlow(config_entry)


class SmartPumpSchedulerOptionsFlow(config_entries.OptionsFlow):
    """Handle options (reconfigure after setup)."""

    def __init__(self, config_entry):
        self._entry = config_entry
        self._data = dict(config_entry.data)

    async def async_step_init(self, user_input=None):
        """Show options menu."""
        return await self.async_step_pump_settings()

    async def async_step_pump_settings(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_schedule()

        current = self._entry.data
        return self.async_show_form(
            step_id="pump_settings",
            data_schema=vol.Schema({
                vol.Required(CONF_HOURS_PER_DAY, default=current.get(CONF_HOURS_PER_DAY, DEFAULT_HOURS_PER_DAY)): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=1, max=24, step=1, mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Optional(CONF_MIN_PRICE, default=current.get(CONF_MIN_PRICE)): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=500, step=1, mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Optional(CONF_MAX_PRICE, default=current.get(CONF_MAX_PRICE)): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=500, step=1, mode=selector.NumberSelectorMode.BOX)
                ),
            }),
        )

    async def async_step_schedule(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="", data=self._data)

        current = self._entry.data
        schema_dict = {
            vol.Required(CONF_PER_WEEKDAY, default=current.get(CONF_PER_WEEKDAY, False)): selector.BooleanSelector(),
            vol.Required(CONF_GLOBAL_START, default=current.get(CONF_GLOBAL_START, DEFAULT_GLOBAL_START)): selector.TimeSelector(),
            vol.Required(CONF_GLOBAL_STOP, default=current.get(CONF_GLOBAL_STOP, DEFAULT_GLOBAL_STOP)): selector.TimeSelector(),
        }
        for day in WEEKDAYS:
            schema_dict[vol.Optional(f"{day}_active", default=current.get(f"{day}_active", True))] = selector.BooleanSelector()
            schema_dict[vol.Optional(f"{day}_start", default=current.get(f"{day}_start", "06:00"))] = selector.TimeSelector()
            schema_dict[vol.Optional(f"{day}_stop", default=current.get(f"{day}_stop", "22:00"))] = selector.TimeSelector()

        return self.async_show_form(
            step_id="schedule",
            data_schema=vol.Schema(schema_dict),
        )
