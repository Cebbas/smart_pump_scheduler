<p align="center"><img src="logo.png" alt="Smart Pump Scheduler" width="420"></p>

[🇬🇧 English](README.md) | **🇸🇪 Svenska** | [🇳🇴 Norsk](README.no.md) | [🇫🇮 Suomi](README.fi.md) | [🇩🇰 Dansk](README.da.md) | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | [🇳🇱 Nederlands](README.nl.md)

---

# Smart Pump Scheduler

En Home Assistant-integration (HACS) som optimerar din pumps körtider baserat på elpriser.

## Funktioner

- 🔌 **Flexibel priskälla** – Nordpool (automatiskt), valfri HA-sensor (Tibber m.fl.) eller fast schema
- ⏰ **Smart schemaläggning** – kör under de N billigaste timmarna per dygn
- 📅 **Styrning per veckodag** – olika timmar, tidsfönster eller inaktivera helt per dag
- 🛁 **Pausfunktion** – pausa för bad och schemalägg automatiskt om en ersättningstimme
- ⚡ **Energispårning** – riktig sensor eller manuell watt-inställning, beräknar kostnad och besparing
- 🌍 **Flerspråkig** – följer Home Assistants språkinställning (SV, EN, NO, FI, DA, DE, FR, NL)
- 💰 **Prisgränser** – kör alltid under X öre, kör aldrig över Y öre

## Installation via HACS

1. Öppna HACS i Home Assistant
2. Gå till **Integrationer** → tre-punktsmenyn → **Anpassade arkiv**
3. Lägg till `https://github.com/Cebbas/smart_pump_scheduler` som en **Integration**
4. Installera **Smart Pump Scheduler**
5. Starta om Home Assistant
6. Gå till **Inställningar → Enheter & tjänster → Lägg till integration → Smart Pump Scheduler**

## Manuell installation (utan HACS)

1. Ladda ner det här repot som en ZIP (**Code → Download ZIP** på GitHub, eller en release-ZIP från [Releases-sidan](https://github.com/Cebbas/smart_pump_scheduler/releases))
2. Kopiera mappen `custom_components/smart_pump_scheduler` till din Home Assistants `config/custom_components/`-mapp, så att du får `config/custom_components/smart_pump_scheduler/manifest.json`
3. Starta om Home Assistant
4. Gå till **Inställningar → Enheter & tjänster → Lägg till integration → Smart Pump Scheduler**

Du behöver upprepa steg 1–3 manuellt vid framtida uppdateringar, eftersom HACS normalt sköter det automatiskt.

## Konfiguration

Integrationen konfigureras helt via gränssnittet – ingen YAML-redigering krävs.

### Steg 1 – Priskälla

Du namnger även pumpen först (praktiskt om du sätter upp fler än en).

| Alternativ | Beskrivning |
|---|---|
| Nordpool | Hämtar priser automatiskt. Välj område (SE1–SE4, NO, DK, FI...) och valuta. |
| HA-sensor | Använd en befintlig sensor från Nordpool, Tibber eller annan integration. |
| Fast schema | Ingen prisoptimering – kör på ett fast tidsfönster. |

### Steg 2 – Pumpinställningar
- Välj den switch-entitet som styr din pump
- Ange antal timmar per dygn (1–24)
- Valfritt: kör alltid under X öre/kWh
- Valfritt: kör aldrig över Y öre/kWh

### Steg 3 – Schema
- Globalt tidsfönster (t.ex. 06:00–22:00)
- Eller aktivera per-veckodag med individuella start/stopp-tider och timmar
- Inaktivera specifika dagar helt

### Steg 4 – Pausinställningar
- Aktivera/inaktivera pausfunktionen
- Ange pauslängd (standard 60 min)
- Ange max antal pauser per dygn

### Steg 5 – Energimätning
- Koppla en energi/effektsensor från din smarta stickpropp
- Eller ange pumpens effektförbrukning manuellt i watt
- Används för kostnads- och besparingsberäkningar

## Entiteter som skapas

| Entitet | Beskrivning |
|---|---|
| `binary_sensor.pump_schema` | PÅ när pumpen ska köra |
| `sensor.pump_aktuellt_pris` | Aktuellt elpris |
| `sensor.pump_nasta_start` | Nästa schemalagda start |
| `sensor.pump_timmar_kvar_idag` | Schemalagda timmar kvar idag |
| `sensor.pump_scheduled_hours_today` | Dagens schemalagda timmar, som tidsintervall |
| `sensor.pump_energi_idag` | Förbrukad energi idag (kWh) |
| `sensor.pump_drifttid_idag` | Faktisk tid pumpen har körts idag |
| `sensor.pump_kostnad_idag` | Kostnad idag |
| `sensor.pump_sparade_kronor` | Besparing vs körning på dyra timmar |
| `sensor.pump_effekt` | Aktuell effekt |
| `switch.pump_paus` | Toggla paus på/av |
| `button.pump_pausa` | Pausa under konfigurerad tid |
| `number.pump_timmar_per_dygn` | Justera dagliga timmar från dashboard |

## Tjänster

| Tjänst | Beskrivning |
|---|---|
| `smart_pump_scheduler.pausa` | Pausa pumpen N minuter |
| `smart_pump_scheduler.aterstall` | Avbryt paus, återgå till schema |
| `smart_pump_scheduler.uppdatera_schema` | Tvinga omräkning av dagens schema |

## Dashboard-kort exempel

```yaml
type: entities
title: Smart pumpschemaläggare
entities:
  - entity: binary_sensor.pump_schema
    name: Körs nu
  - entity: number.pump_timmar_per_dygn
    name: Timmar per dygn
  - entity: sensor.pump_aktuellt_pris
    name: Aktuellt pris
  - entity: sensor.pump_nasta_start
    name: Nästa start
  - entity: button.pump_pausa
    name: 🛁 Pausa för bad
  - entity: sensor.pump_sparade_kronor
    name: Sparat idag
  - entity: sensor.pump_kostnad_idag
    name: Kostnad idag
```

## Visualisera dagens schema

Integrationen kan inte lägga till en graf på sin egen sida under Enheter & tjänster — den sidan är låst av Home Assistants kärna och visar bara entiteter och diagnostik. Grafer hör istället hemma på en dashboard, där du har två alternativ:

### Alternativ A – Inga extra beroenden

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

### Alternativ B – Graf (kräver [apexcharts-card](https://github.com/RomRider/apexcharts-card) från HACS)

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

## Stödda språk

English (en), Svenska (sv), Norsk (no), Suomi (fi), Dansk (da), Deutsch (de), Français (fr), Nederlands (nl)

## Licens

MIT
