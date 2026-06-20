<p align="center"><img src="logo.png" alt="Smart Pump Scheduler" width="420"></p>

[🇬🇧 English](README.md) | [🇸🇪 Svenska](README.sv.md) | [🇳🇴 Norsk](README.no.md) | [🇫🇮 Suomi](README.fi.md) | **🇩🇰 Dansk** | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | [🇳🇱 Nederlands](README.nl.md)

<p align="center">
  <a href="https://buymeacoffee.com/h7jyzdywm9s"><img src="https://img.shields.io/badge/Buy%20me%20a%20coffee-FFDD00?style=flat&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee"></a>
</p>

---

# Smart Pump Scheduler

En Home Assistant-integration (HACS), der optimerer pumpens driftstimer baseret på elpriser.

## Funktioner

- 🔌 **Fleksibel priskilde** – Nordpool (automatisk), valgfri HA-sensor (Tibber m.fl.) eller fast tidsplan
- ⏰ **Smart planlægning** – kører i de N billigste timer pr. døgn
- 📅 **Styring pr. ugedag** – forskellige timer, tidsvinduer eller deaktiver helt pr. dag
- 🛁 **Pausefunktion** – sæt på pause til bad og planlæg automatisk en erstatningstime
- ▶️ **Kør nu** – kør i en valgbar varighed på forespørsel (f.eks. efter bad), venter automatisk til prisen falder under din maksgrænse
- ⚡ **Energisporing** – rigtig sensor eller manuel watt-indstilling, beregner omkostninger og besparelser
- 🌍 **Flersproget** – følger Home Assistants sprogindstilling (DA, EN, SV, NO, FI, DE, FR, NL)
- 💰 **Prisgrænser** – kør altid under X øre, kør aldrig over Y øre

## Installation via HACS

1. Åbn HACS i Home Assistant
2. Gå til **Integrationer** → tre-punktsmenuen → **Brugerdefinerede arkiver**
3. Tilføj `https://github.com/Cebbas/smart_pump_scheduler` som en **Integration**
4. Installer **Smart Pump Scheduler**
5. Genstart Home Assistant
6. Gå til **Indstillinger → Enheder & tjenester → Tilføj integration → Smart Pump Scheduler**

## Manuel installation (uden HACS)

1. Download dette repo som en ZIP (**Code → Download ZIP** på GitHub, eller en release-ZIP fra [udgivelsessiden](https://github.com/Cebbas/smart_pump_scheduler/releases))
2. Kopier mappen `custom_components/smart_pump_scheduler` til din Home Assistants `config/custom_components/`-mappe, så du ender med `config/custom_components/smart_pump_scheduler/manifest.json`
3. Genstart Home Assistant
4. Gå til **Indstillinger → Enheder & tjenester → Tilføj integration → Smart Pump Scheduler**

Du skal gentage trin 1-3 manuelt ved fremtidige opdateringer, da HACS normalt klarer det automatisk.

## Konfiguration

Integrationen konfigureres helt via grænsefladen – ingen YAML-redigering kræves.

### Trin 1 – Priskilde

Du navngiver også pumpen først (nyttigt hvis du opsætter mere end en).

| Mulighed | Beskrivelse |
|---|---|
| Nordpool | Henter priser automatisk. Vælg område (DK1–DK2, SE, NO, FI...) og valuta. |
| HA-sensor | Brug en eksisterende sensor fra Nordpool, Tibber eller en anden integration. |
| Fast tidsplan | Ingen prisoptimering – kører i et fast tidsvindue. |

### Trin 2 – Pumpeindstillinger
- Vælg den switch-entitet, der styrer pumpen
- Angiv antal timer pr. døgn (1–24)
- Valgfrit: kør altid under X øre/kWh
- Valgfrit: kør aldrig over Y øre/kWh

### Trin 3 – Tidsplan
- Globalt tidsvindue (f.eks. 06:00–22:00)
- Eller aktiver pr.-ugedag med individuelle start/stop-tider og timer
- Deaktiver specifikke dage helt

### Trin 4 – Pause- og kør nu-indstillinger
- Aktiver/deaktiver pausefunktionen
- Angiv pausevarighed (standard 60 min)
- Angiv maks. antal pauser pr. døgn
- Angiv kør nu-varighed (standard 30 min) – bruges af knappen/tjenesten "Kør nu"

### Trin 5 – Energimåling
- Tilslut en energi/effektsensor fra din smarte stikkontakt
- Eller angiv pumpens effektforbrug manuelt i watt
- Bruges til omkostnings- og besparelsesberegninger

## Oprettede entiteter

| Entitet | Beskrivelse |
|---|---|
| `binary_sensor.pump_schema` | TIL når pumpen skal køre |
| `sensor.pump_aktuellt_pris` | Aktuel elpris |
| `sensor.pump_nasta_start` | Næste planlagte start |
| `sensor.pump_timmar_kvar_idag` | Planlagte timer tilbage i dag |
| `sensor.pump_scheduled_hours_today` | Dagens planlagte timer, som tidsintervaller |
| `sensor.pump_energi_idag` | Forbrugt energi i dag (kWh) |
| `sensor.pump_drifttid_idag` | Faktisk tid pumpen har kørt i dag (minutter, med formateret "h min"-attribut) |
| `sensor.pump_kostnad_idag` | Omkostninger i dag |
| `sensor.pump_sparade_kronor` | Besparelse vs. kørsel på dyre timer |
| `sensor.pump_effekt` | Aktuel effekt |
| `switch.pump_paus` | Skift pause til/fra |
| `button.pump_pausa` | Pause i konfigureret tid |
| `button.pump_kor_nu` | Kør nu i konfigureret tid (venter hvis prisen er over maks) |
| `number.pump_timmar_per_dygn` | Juster daglige timer fra dashboard |
| `number.pump_kor_nu_minuter` | Juster kør nu-varigheden fra dashboard |

## Tjenester

| Tjeneste | Beskrivelse |
|---|---|
| `smart_pump_scheduler.pausa` | Sæt pumpen på pause i N minutter |
| `smart_pump_scheduler.aterstall` | Annullér pause, returner til tidsplan |
| `smart_pump_scheduler.uppdatera_schema` | Gennemtving omberegning af dagens tidsplan |
| `smart_pump_scheduler.kor_nu` | Kør nu i N minutter (venter hvis prisen er over maks) |

## Advarsler & notifikationer

| Situation | Hvor du ser det |
|---|---|
| Dagens ønskede timer kan ikke være inden for tidsvinduet/prisgrænserne | **Indstillinger → System → Reparationer** ("Kunne ikke planlægge alle timer") |
| En "Kør nu"-anmodning venter, fordi prisen er over maksgrænsen | **Indstillinger → System → Reparationer** ("Venter på lavere pris for at køre på forespørsel") |
| En ventende "Kør nu"-anmodning starter faktisk, når prisen falder | En notifikation (klokkeikon / companion-app) |

Begge reparationsadvarsler forsvinder automatisk, når de er løst.

## Dashboard-kort eksempel

```yaml
type: entities
title: Smart pumpplanlægger
entities:
  - entity: binary_sensor.pump_schema
    name: Kører nu
  - entity: number.pump_timmar_per_dygn
    name: Timer pr. døgn
  - entity: sensor.pump_aktuellt_pris
    name: Aktuel pris
  - entity: sensor.pump_nasta_start
    name: Næste start
  - entity: button.pump_pausa
    name: 🛁 Pause til bad
  - entity: button.pump_kor_nu
    name: ▶️ Kør nu
  - entity: sensor.pump_sparade_kronor
    name: Sparet i dag
  - entity: sensor.pump_kostnad_idag
    name: Omkostninger i dag
```

## Visualisering af dagens plan

Integrationen kan ikke tilføje en graf til sin egen side under Enheder & tjenester — den side er låst af Home Assistants kerne og viser kun entiteter og diagnostik. Grafer hører i stedet hjemme på et dashboard, hvor du har to muligheder:

### Mulighed A – Ingen ekstra afhængigheder

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

### Mulighed B – Graf (kræver [apexcharts-card](https://github.com/RomRider/apexcharts-card) fra HACS)

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

## Understøttede sprog

English (en), Svenska (sv), Norsk (no), Suomi (fi), Dansk (da), Deutsch (de), Français (fr), Nederlands (nl)

## Licens

MIT
