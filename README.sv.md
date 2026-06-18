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

## Konfiguration

Integrationen konfigureras helt via gränssnittet – ingen YAML-redigering krävs.

### Steg 1 – Priskälla
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
| `sensor.pump_energi_idag` | Förbrukad energi idag (kWh) |
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

## Stödda språk

English (en), Svenska (sv), Norsk (no), Suomi (fi), Dansk (da), Deutsch (de), Français (fr), Nederlands (nl)

## Licens

MIT
