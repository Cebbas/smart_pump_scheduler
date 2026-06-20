"""Constants for Smart Pump Scheduler integration."""

DOMAIN = "smart_pump_scheduler"
VERSION = "1.3.2"

# Config flow keys
CONF_PRICE_SOURCE = "price_source"
CONF_NORDPOOL_AREA = "nordpool_area"
CONF_NORDPOOL_CURRENCY = "nordpool_currency"
CONF_NORDPOOL_VAT = "nordpool_vat"
CONF_PRICE_SENSOR = "price_sensor"
CONF_SWITCH_ENTITY = "switch_entity"
CONF_HOURS_PER_DAY = "hours_per_day"
CONF_MIN_PRICE = "min_price"
CONF_MAX_PRICE = "max_price"
CONF_PER_WEEKDAY = "per_weekday"
CONF_GLOBAL_START = "global_start"
CONF_GLOBAL_STOP = "global_stop"
CONF_WEEKDAY_SCHEDULE = "weekday_schedule"
CONF_ENABLE_PAUSE = "enable_pause"
CONF_PAUSE_DURATION = "pause_duration"
CONF_MAX_PAUSES = "max_pauses"
CONF_ENERGY_SOURCE = "energy_source"
CONF_ENERGY_SENSOR = "energy_sensor"
CONF_MANUAL_WATT = "manual_watt"
CONF_RUN_NOW_DURATION = "run_now_duration"

# Price sources
PRICE_SOURCE_NORDPOOL = "nordpool"
PRICE_SOURCE_SENSOR = "sensor"
PRICE_SOURCE_FIXED = "fixed"

# Energy sources
ENERGY_SOURCE_SENSOR = "sensor"
ENERGY_SOURCE_MANUAL = "manual"
ENERGY_SOURCE_NONE = "none"

# Nordpool areas
NORDPOOL_AREAS = [
    "SE1", "SE2", "SE3", "SE4",
    "NO1", "NO2", "NO3", "NO4", "NO5",
    "DK1", "DK2",
    "FI",
    "EE", "LV", "LT",
]

# Currencies
NORDPOOL_CURRENCIES = ["SEK", "NOK", "EUR", "DKK"]

# Weekdays
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
WEEKDAY_LABELS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

# Nordpool API
NORDPOOL_API_URL = "https://dataportal-api.nordpoolgroup.com/api/DayAheadPrices"
NORDPOOL_API_CURRENCY_MAP = {
    "SEK": "SEK",
    "NOK": "NOK",
    "EUR": "EUR",
    "DKK": "DKK",
}

# Defaults
DEFAULT_HOURS_PER_DAY = 4
DEFAULT_PAUSE_DURATION = 60
DEFAULT_MAX_PAUSES = 3
DEFAULT_GLOBAL_START = "00:00"
DEFAULT_GLOBAL_STOP = "00:00"
DEFAULT_MANUAL_WATT = 350
DEFAULT_RUN_NOW_DURATION = 30

# Update intervals
SCHEDULE_UPDATE_HOUR = 0
SCHEDULE_UPDATE_MINUTE = 5
PRICE_RETRY_INTERVAL = 15  # minutes
COORDINATOR_UPDATE_INTERVAL = 60  # seconds

# Storage keys
STORAGE_KEY = f"{DOMAIN}.schedule"
STORAGE_VERSION = 1

# Entity unique id suffixes
SUFFIX_SCHEMA = "schema"
SUFFIX_CURRENT_PRICE = "current_price"
SUFFIX_NEXT_START = "next_start"
SUFFIX_HOURS_REMAINING = "hours_remaining"
SUFFIX_SCHEDULED_HOURS = "scheduled_hours"
SUFFIX_ENERGY_TODAY = "energy_today"
SUFFIX_RUNTIME_TODAY = "runtime_today"
SUFFIX_COST_TODAY = "cost_today"
SUFFIX_SAVED_TODAY = "saved_today"
SUFFIX_POWER = "power"
SUFFIX_PAUSE_SWITCH = "pause_switch"
SUFFIX_PAUSE_BUTTON = "pause_button"
SUFFIX_HOURS_NUMBER = "hours_number"
SUFFIX_RUN_NOW_BUTTON = "run_now_button"
SUFFIX_RUN_NOW_NUMBER = "run_now_number"

# Platforms
PLATFORMS = ["binary_sensor", "sensor", "switch", "button", "number"]
