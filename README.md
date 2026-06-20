<p align="center"><img src="logo.png" alt="Smart Pump Scheduler" width="420"></p>

🌍 **English** | [Svenska](README.sv.md) | [Norsk](README.no.md) | [Suomi](README.fi.md) | [Dansk](README.da.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Nederlands](README.nl.md)

<p align="center">
  <a href="https://buymeacoffee.com/h7jyzdywm9s"><img src="https://img.shields.io/badge/Buy%20me%20a%20coffee-FFDD00?style=flat&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee"></a>
</p>

---

# Smart Pump Scheduler

A Home Assistant custom integration (HACS) that optimizes your pump's running hours based on electricity prices.

## Features

- 🔌 **Flexible price sources** – Nordpool (automatic), any HA sensor (Tibber, etc.), or fixed schedule
- ⏰ **Smart scheduling** – runs during the cheapest N hours per day
- 📅 **Per-weekday control** – different hours, time windows, or disable entirely per day
- 🛁 **Pause function** – pause for bathing and automatically reschedule a compensating hour
- ▶️ **Run now** – run for a configurable duration on demand (e.g. after bathing), deferred automatically until the price drops below your max threshold
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

## Manual installation (without HACS)

1. Download this repository as a ZIP (**Code → Download ZIP** on GitHub, or a release ZIP from the [Releases page](https://github.com/Cebbas/smart_pump_scheduler/releases))
2. Copy the `custom_components/smart_pump_scheduler` folder into your Home Assistant's `config/custom_components/` folder, so you end up with `config/custom_components/smart_pump_scheduler/manifest.json`
3. Restart Home Assistant
4. Go to **Settings → Devices & Services → Add Integration → Smart Pump Scheduler**

You'll need to repeat steps 1–3 manually for future updates, since HACS normally handles that automatically.

## Configuration

The integration is configured entirely through the UI – no YAML editing required.

### Step 1 – Price source

You'll also give the pump a name first (handy if you set up more than one).

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

### Step 4 – Pause & run now settings
- Enable/disable the pause function
- Set pause duration (default 60 min)
- Set max pauses per day
- Set run now duration (default 30 min) – used by the "Run now" button/service

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
| `sensor.pump_scheduled_hours_today` | Today's scheduled hours, as time ranges |
| `sensor.pump_energy_today` | Energy consumed today (kWh) |
| `sensor.pump_runtime_today` | Actual time the pump has run today (minutes, with an "h min" formatted attribute) |
| `sensor.pump_cost_today` | Cost today (in your currency) |
| `sensor.pump_saved_today` | Savings vs running at peak hours |
| `sensor.pump_power` | Current power draw |
| `switch.pump_pause` | Toggle pause on/off |
| `button.pump_pause` | Pause for configured duration |
| `button.pump_run_now` | Run now for the configured duration (deferred if price is above max) |
| `number.pump_hours_per_day` | Adjust daily hours from dashboard |
| `number.pump_run_now_minutes` | Adjust the "Run now" duration from dashboard |

## Services

| Service | Description |
|---|---|
| `smart_pump_scheduler.pausa` | Pause pump for N minutes |
| `smart_pump_scheduler.aterstall` | Cancel pause, return to schedule |
| `smart_pump_scheduler.uppdatera_schema` | Force recalculate today's schedule |
| `smart_pump_scheduler.kor_nu` | Run now for N minutes (deferred if price is above max) |

## Warnings & notifications

| Situation | Where you'll see it |
|---|---|
| Today's requested hours don't fully fit the time window/price limits | **Settings → System → Repairs** ("Couldn't schedule all hours") |
| A "Run now" request is queued because the price is above the max threshold | **Settings → System → Repairs** ("Waiting for a cheaper price to run on demand") |
| A queued "Run now" request actually starts once the price drops | A persistent notification (bell icon / companion app) |

Both Repairs issues clear themselves automatically once resolved.

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
  - entity: button.pump_run_now
    name: ▶️ Run now
  - entity: sensor.pump_saved_today
    name: Saved today
  - entity: sensor.pump_cost_today
    name: Cost today
```

## Visualizing today's schedule

The integration can't add a chart to its own Devices & Services page — that page is fixed by Home Assistant core and only shows entities and diagnostics. Charts belong on a dashboard instead, where you have two options:

### Option A – No extra dependencies

```yaml
type: markdown
title: Today's plan
content: >
  {% set sched = state_attr('sensor.pump_scheduled_hours_today', 'hours') or [] %}
  {% set prices = state_attr('sensor.pump_scheduled_hours_today', 'prices') or {} %}
  {% set rows = [] %}
  {% for h, price in prices.items() %}
    {% set rows = rows + [(h | int, price)] %}
  {% endfor %}
  | Hour | Price | Running |
  |---|---|---|
  {% for h, price in rows | sort %}
  | {{ '%02d:00' | format(h) }} | {{ price }} | {{ '🟢' if h in sched else '⚪' }} |
  {% endfor %}
```

### Option B – Graph (requires [apexcharts-card](https://github.com/RomRider/apexcharts-card) from HACS)

```yaml
type: custom:apexcharts-card
header:
  title: Price vs. scheduled hours
  show: true
graph_span: 24h
span:
  start: day
series:
  - entity: sensor.pump_scheduled_hours_today
    name: Price
    type: column
    data_generator: |
      const prices = entity.attributes.prices || {};
      return Object.entries(prices).map(([h, p]) => [
        new Date().setHours(parseInt(h), 0, 0, 0), p
      ]);
  - entity: sensor.pump_scheduled_hours_today
    name: Running
    type: column
    color: '#02B875'
    data_generator: |
      const hours = entity.attributes.hours || [];
      return hours.map(h => [
        new Date().setHours(h, 0, 0, 0), 1
      ]);
```

## Supported languages

English (en), Svenska (sv), Norsk (no), Suomi (fi), Dansk (da), Deutsch (de), Français (fr), Nederlands (nl)

## License

MIT
