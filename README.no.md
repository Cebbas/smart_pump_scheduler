<p align="center"><img src="logo.png" alt="Smart Pump Scheduler" width="420"></p>

[🇬🇧 English](README.md) | [🇸🇪 Svenska](README.sv.md) | **🇳🇴 Norsk** | [🇫🇮 Suomi](README.fi.md) | [🇩🇰 Dansk](README.da.md) | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | [🇳🇱 Nederlands](README.nl.md)

---

# Smart Pump Scheduler

En Home Assistant-integrasjon (HACS) som optimaliserer pumpens kjøretider basert på strømpriser.

## Funksjoner

- 🔌 **Fleksibel priskilde** – Nordpool (automatisk), valgfri HA-sensor (Tibber m.fl.) eller fast tidsplan
- ⏰ **Smart planlegging** – kjører i løpet av de N billigste timene per døgn
- 📅 **Styring per ukedag** – ulike timer, tidsvinduer eller deaktiver helt per dag
- 🛁 **Pausefunksjon** – sett på pause for bading og planlegg automatisk en erstatningsttime
- ▶️ **Kjør nå** – kjør i en valgbar lengde på forespørsel (f.eks. etter bading), venter automatisk til prisen går under maksgrensen din
- ⚡ **Energisporing** – ekte sensor eller manuell watt-innstilling, beregner kostnad og besparelse
- 🌍 **Flerspråklig** – følger Home Assistants språkinnstilling (NO, EN, SV, FI, DA, DE, FR, NL)
- 💰 **Prisgrenser** – kjør alltid under X øre, kjør aldri over Y øre

## Installasjon via HACS

1. Åpne HACS i Home Assistant
2. Gå til **Integrasjoner** → tre-punktsmenyen → **Egendefinerte arkiver**
3. Legg til `https://github.com/Cebbas/smart_pump_scheduler` som en **Integrasjon**
4. Installer **Smart Pump Scheduler**
5. Start Home Assistant på nytt
6. Gå til **Innstillinger → Enheter & tjenester → Legg til integrasjon → Smart Pump Scheduler**

## Manuell installasjon (uten HACS)

1. Last ned dette repoet som en ZIP (**Code → Download ZIP** på GitHub, eller en release-ZIP fra [utgivelsessiden](https://github.com/Cebbas/smart_pump_scheduler/releases))
2. Kopier mappen `custom_components/smart_pump_scheduler` til Home Assistants `config/custom_components/`-mappe, slik at du får `config/custom_components/smart_pump_scheduler/manifest.json`
3. Start Home Assistant på nytt
4. Gå til **Innstillinger → Enheter og tjenester → Legg til integrasjon → Smart Pump Scheduler**

Du må gjenta trinn 1–3 manuelt ved fremtidige oppdateringer, siden HACS normalt gjør dette automatisk.

## Konfigurasjon

Integrasjonen konfigureres helt via grensesnittet – ingen YAML-redigering kreves.

### Trinn 1 – Priskilde

Du gir også pumpen et navn først (nyttig hvis du setter opp flere enn en).

| Alternativ | Beskrivelse |
|---|---|
| Nordpool | Henter priser automatisk. Velg område (NO1–NO5, SE, DK, FI...) og valuta. |
| HA-sensor | Bruk en eksisterende sensor fra Nordpool, Tibber eller annen integrasjon. |
| Fast tidsplan | Ingen prisoptimalisering – kjører på et fast tidsvindu. |

### Trinn 2 – Pumpeinnstillinger
- Velg switch-enheten som styrer pumpen din
- Angi antall timer per døgn (1–24)
- Valgfritt: kjør alltid under X øre/kWh
- Valgfritt: kjør aldri over Y øre/kWh

### Trinn 3 – Tidsplan
- Globalt tidsvindu (f.eks. 06:00–22:00)
- Eller aktiver per-ukedag med individuelle start/stopp-tider og timer
- Deaktiver spesifikke dager helt

### Trinn 4 – Pause- og kjør nå-innstillinger
- Aktiver/deaktiver pausefunksjonen
- Angi pauselengde (standard 60 min)
- Angi maks antall pauser per døgn
- Angi kjør nå-lengde (standard 30 min) – brukes av knappen/tjenesten "Kjør nå"

### Trinn 5 – Energimåling
- Koble til en energi/effektsensor fra din smarte stikkontakt
- Eller angi pumpens effektforbruk manuelt i watt
- Brukes til kostnads- og besparingsberegninger

## Entiteter som opprettes

| Entitet | Beskrivelse |
|---|---|
| `binary_sensor.pump_schema` | PÅ når pumpen skal kjøre |
| `sensor.pump_aktuellt_pris` | Gjeldende strømpris |
| `sensor.pump_nasta_start` | Neste planlagte start |
| `sensor.pump_timmar_kvar_idag` | Planlagte timer igjen i dag |
| `sensor.pump_scheduled_hours_today` | Dagens planlagte timer, som tidsintervaller |
| `sensor.pump_energi_idag` | Forbrukt energi i dag (kWh) |
| `sensor.pump_drifttid_idag` | Faktisk tid pumpen har kjørt i dag (minutter, med formatert "h min"-attributt) |
| `sensor.pump_kostnad_idag` | Kostnad i dag |
| `sensor.pump_sparade_kronor` | Besparelse vs kjøring på dyre timer |
| `sensor.pump_effekt` | Gjeldende effekt |
| `switch.pump_paus` | Veksle pause på/av |
| `button.pump_pausa` | Pause i konfigurert tid |
| `button.pump_kor_nu` | Kjør nå i konfigurert tid (venter hvis prisen er over maks) |
| `number.pump_timmar_per_dygn` | Juster daglige timer fra dashbord |
| `number.pump_kor_nu_minuter` | Juster kjør nå-lengden fra dashbord |

## Tjenester

| Tjeneste | Beskrivelse |
|---|---|
| `smart_pump_scheduler.pausa` | Sett pumpen på pause N minutter |
| `smart_pump_scheduler.aterstall` | Avbryt pause, returner til tidsplan |
| `smart_pump_scheduler.uppdatera_schema` | Tving omberegning av dagens tidsplan |
| `smart_pump_scheduler.kor_nu` | Kjør nå i N minutter (venter hvis prisen er over maks) |

## Dashboard-kort eksempel

```yaml
type: entities
title: Smart pumpplanlegger
entities:
  - entity: binary_sensor.pump_schema
    name: Kjører nå
  - entity: number.pump_timmar_per_dygn
    name: Timer per døgn
  - entity: sensor.pump_aktuellt_pris
    name: Gjeldende pris
  - entity: sensor.pump_nasta_start
    name: Neste start
  - entity: button.pump_pausa
    name: 🛁 Pause for bading
  - entity: button.pump_kor_nu
    name: ▶️ Kjør nå
  - entity: sensor.pump_sparade_kronor
    name: Spart i dag
  - entity: sensor.pump_kostnad_idag
    name: Kostnad i dag
```

## Visualisere dagens plan

Integrasjonen kan ikke legge til en graf på sin egen side under Enheter og tjenester — den siden er låst av Home Assistant-kjernen og viser bare enheter og diagnostikk. Grafer hører heller hjemme på et dashboard, der du har to alternativer:

### Alternativ A – Ingen ekstra avhengigheter

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

### Alternativ B – Graf (krever [apexcharts-card](https://github.com/RomRider/apexcharts-card) fra HACS)

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

## Støttede språk

English (en), Svenska (sv), Norsk (no), Suomi (fi), Dansk (da), Deutsch (de), Français (fr), Nederlands (nl)

## Lisens

MIT
