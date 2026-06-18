<p align="center"><img src="logo.png" alt="Smart Pump Scheduler" width="420"></p>

🌍 **English** | [Svenska](README.sv.md) | [Norsk](README.no.md) | [Suomi](README.fi.md) | [Dansk](README.da.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Nederlands](README.nl.md)

---

# Smart Pump Scheduler

A Home Assistant custom integration (HACS) that optimizes your pump's running hours based on electricity prices.

## Features

- 🔌 **Flexible price sources** – Nordpool (automatic), any HA sensor (Tibber, etc.), or fixed schedule
- ⏰ **Smart scheduling** – runs during the cheapest N hours per day
- 📅 **Per-weekday control** – different hours, time windows, or disable entirely per day
- 🛁 **Pause function** – pause for bathing and automatically reschedule a compensating hour
- ⚡ **Energy tracking** – real sensor or manual watt setting, calculates cost and savings
- 🌍 **Multilingual** – follows Home Assistant's language setting (EN, SV, NO, FI, DA, DE, FR, NL)
- 💰 **Price guards** – always run below X öre, never run above Y öre

## Installation via HACS

1. Open HACS in Home Assistant
2. Go to **Integrations** → three-dot menu → **Custom repositories**
3. Add `https://github.com/Cebbas/smart_pump_scheduler` as an **Integration**
4. Install **Smart Pump Scheduler**
5. Restart Home Assistant
6. Go to **Settings → Devices & Services → Add Integration → Smart Pump Scheduler**

## Configuration

The integration is configured entirely through the UI – no YAML editing required.

### Step 1 – Price source
| Option | Description |
|---|---|
| Nordpool | Fetches prices automatically. Choose area (SE1–SE4, NO, DK, FI...) and currency. |
| HA Sensor | Use an existing sensor from Nordpool, Tibber, or any other integration. |
| Fixed schedule | No price optimization – runs on a fixed time window. |

### Step 2 – Pump settings
- Select the switch entity controlling your pump
- Set default hours per day (1–24)
- Optional: always run below X öre/kWh
- Optional: never run above Y öre/kWh

### Step 3 – Schedule
- Global time window (e.g. 06:00–22:00)
- Or enable per-weekday settings with individual start/stop times and hours
- Deactivate specific days entirely

### Step 4 – Pause settings
- Enable/disable the pause function
- Set pause duration (default 60 min)
- Set max pauses per day

### Step 5 – Energy monitoring
- Connect an energy/power sensor from your smart plug
- Or enter the pump's power consumption manually in watts
- Used for cost and savings calculations

## Entities created

| Entity | Description |
|---|---|
| `binary_sensor.pump_schedule` | ON when pump should be running |
| `sensor.pump_current_price` | Current electricity price |
| `sensor.pump_next_start` | Next scheduled start time |
| `sensor.pump_hours_remaining` | Scheduled hours remaining today |
| `sensor.pump_energy_today` | Energy consumed today (kWh) |
| `sensor.pump_cost_today` | Cost today (in your currency) |
| `sensor.pump_saved_today` | Savings vs running at peak hours |
| `sensor.pump_power` | Current power draw |
| `switch.pump_pause` | Toggle pause on/off |
| `button.pump_pause` | Pause for configured duration |
| `number.pump_hours_per_day` | Adjust daily hours from dashboard |

## Services

| Service | Description |
|---|---|
| `smart_pump_scheduler.pausa` | Pause pump for N minutes |
| `smart_pump_scheduler.aterstall` | Cancel pause, return to schedule |
| `smart_pump_scheduler.uppdatera_schema` | Force recalculate today's schedule |

## Dashboard card example

```yaml
type: entities
title: Smart Pump Scheduler
entities:
  - entity: binary_sensor.pump_schedule
    name: Running now
  - entity: number.pump_hours_per_day
    name: Hours per day
  - entity: sensor.pump_current_price
    name: Current price
  - entity: sensor.pump_next_start
    name: Next start
  - entity: button.pump_pause
    name: 🛁 Pause for bathing
  - entity: sensor.pump_saved_today
    name: Saved today
  - entity: sensor.pump_cost_today
    name: Cost today
```

## Supported languages

English (en), Svenska (sv), Norsk (no), Suomi (fi), Dansk (da), Deutsch (de), Français (fr), Nederlands (nl)

## License

MIT
