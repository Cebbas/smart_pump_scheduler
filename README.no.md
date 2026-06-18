[🇬🇧 English](README.md) | [🇸🇪 Svenska](README.sv.md) | **🇳🇴 Norsk** | [🇫🇮 Suomi](README.fi.md) | [🇩🇰 Dansk](README.da.md) | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | [🇳🇱 Nederlands](README.nl.md)

---

# Smart Pump Scheduler 🌿

En Home Assistant-integrasjon (HACS) som optimaliserer pumpens kjøretider basert på strømpriser.

## Funksjoner

- 🔌 **Fleksibel priskilde** – Nordpool (automatisk), valgfri HA-sensor (Tibber m.fl.) eller fast tidsplan
- ⏰ **Smart planlegging** – kjører i løpet av de N billigste timene per døgn
- 📅 **Styring per ukedag** – ulike timer, tidsvinduer eller deaktiver helt per dag
- 🛁 **Pausefunksjon** – sett på pause for bading og planlegg automatisk en erstatningsttime
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

## Konfigurasjon

Integrasjonen konfigureres helt via grensesnittet – ingen YAML-redigering kreves.

### Trinn 1 – Priskilde
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

### Trinn 4 – Pauseinnstillinger
- Aktiver/deaktiver pausefunksjonen
- Angi pauselengde (standard 60 min)
- Angi maks antall pauser per døgn

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
| `sensor.pump_energi_idag` | Forbrukt energi i dag (kWh) |
| `sensor.pump_kostnad_idag` | Kostnad i dag |
| `sensor.pump_sparade_kronor` | Besparelse vs kjøring på dyre timer |
| `sensor.pump_effekt` | Gjeldende effekt |
| `switch.pump_paus` | Veksle pause på/av |
| `button.pump_pausa` | Pause i konfigurert tid |
| `number.pump_timmar_per_dygn` | Juster daglige timer fra dashbord |

## Tjenester

| Tjeneste | Beskrivelse |
|---|---|
| `smart_pump_scheduler.pausa` | Sett pumpen på pause N minutter |
| `smart_pump_scheduler.aterstall` | Avbryt pause, returner til tidsplan |
| `smart_pump_scheduler.uppdatera_schema` | Tving omberegning av dagens tidsplan |

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
  - entity: sensor.pump_sparade_kronor
    name: Spart i dag
  - entity: sensor.pump_kostnad_idag
    name: Kostnad i dag
```

## Støttede språk

English (en), Svenska (sv), Norsk (no), Suomi (fi), Dansk (da), Deutsch (de), Français (fr), Nederlands (nl)

## Lisens

MIT
