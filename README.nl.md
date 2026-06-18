<p align="center"><img src="logo.png" alt="Smart Pump Scheduler" width="420"></p>

[🇬🇧 English](README.md) | [🇸🇪 Svenska](README.sv.md) | [🇳🇴 Norsk](README.no.md) | [🇫🇮 Suomi](README.fi.md) | [🇩🇰 Dansk](README.da.md) | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | **🇳🇱 Nederlands**

---

# Smart Pump Scheduler

Een Home Assistant-integratie (HACS) die de bedrijfstijden van uw pomp optimaliseert op basis van elektriciteitsprijzen.

## Functies

- 🔌 **Flexibele prijsbron** – Nordpool (automatisch), elke HA-sensor (Tibber, enz.) of vast schema
- ⏰ **Slimme planning** – draait tijdens de N goedkoopste uren per dag
- 📅 **Bediening per weekdag** – verschillende uren, tijdvensters of volledig uitschakelen per dag
- 🛁 **Pauze-functie** – pauzeer voor het bad en herplan automatisch een vervangend uur
- ⚡ **Energiebewaking** – echte sensor of handmatige watt-instelling, berekent kosten en besparingen
- 🌍 **Meertalig** – volgt de taalinstelling van Home Assistant (NL, EN, SV, NO, FI, DA, DE, FR)
- 💰 **Prijsgrenzen** – altijd draaien onder X ct, nooit draaien boven Y ct

## Installatie via HACS

1. Open HACS in Home Assistant
2. Ga naar **Integraties** → driepuntsmenu → **Aangepaste opslagplaatsen**
3. Voeg `https://github.com/Cebbas/smart_pump_scheduler` toe als **Integratie**
4. Installeer **Smart Pump Scheduler**
5. Herstart Home Assistant
6. Ga naar **Instellingen → Apparaten & diensten → Integratie toevoegen → Smart Pump Scheduler**

## Configuratie

De integratie wordt volledig geconfigureerd via de gebruikersinterface – geen YAML-bewerking vereist.

### Stap 1 – Prijsbron
| Optie | Beschrijving |
|---|---|
| Nordpool | Haalt prijzen automatisch op. Kies gebied (NL, SE1–SE4, NO, DK, FI...) en valuta. |
| HA-sensor | Gebruik een bestaande sensor van Nordpool, Tibber of een andere integratie. |
| Vast schema | Geen prijsoptimalisatie – draait op een vast tijdvenster. |

### Stap 2 – Pompinstellingen
- Selecteer de schakelaar-entiteit die uw pomp bestuurt
- Stel uren per dag in (1–24)
- Optioneel: altijd draaien onder X ct/kWh
- Optioneel: nooit draaien boven Y ct/kWh

### Stap 3 – Schema
- Globaal tijdvenster (bijv. 06:00–22:00)
- Of schakel per-weekdag-instellingen in met individuele start/stop-tijden en uren
- Schakel specifieke dagen volledig uit

### Stap 4 – Pauze-instellingen
- Pauze-functie in-/uitschakelen
- Pauze-duur instellen (standaard 60 min)
- Max. pauzes per dag instellen

### Stap 5 – Energiemeting
- Verbind een energie/vermogensensor van uw slimme stekker
- Of voer het stroomverbruik van de pomp handmatig in in watt
- Gebruikt voor kosten- en besparingsberekeningen

## Aangemaakte entiteiten

| Entiteit | Beschrijving |
|---|---|
| `binary_sensor.pump_schema` | AAN wanneer de pomp moet draaien |
| `sensor.pump_aktuellt_pris` | Huidige elektriciteitsprijs |
| `sensor.pump_nasta_start` | Volgende geplande start |
| `sensor.pump_timmar_kvar_idag` | Geplande uren resterend vandaag |
| `sensor.pump_energi_idag` | Verbruikte energie vandaag (kWh) |
| `sensor.pump_kostnad_idag` | Kosten vandaag |
| `sensor.pump_sparade_kronor` | Besparing vs. draaien op dure uren |
| `sensor.pump_effekt` | Huidig vermogen |
| `switch.pump_paus` | Pauze aan/uit schakelen |
| `button.pump_pausa` | Pauzeer voor geconfigureerde duur |
| `number.pump_timmar_per_dygn` | Dagelijkse uren aanpassen via dashboard |

## Diensten

| Dienst | Beschrijving |
|---|---|
| `smart_pump_scheduler.pausa` | Pomp N minuten pauzeren |
| `smart_pump_scheduler.aterstall` | Pauze annuleren, terug naar schema |
| `smart_pump_scheduler.uppdatera_schema` | Herberekening van het schema van vandaag forceren |

## Dashboard-kaart voorbeeld

```yaml
type: entities
title: Slimme pompplanner
entities:
  - entity: binary_sensor.pump_schema
    name: Draait nu
  - entity: number.pump_timmar_per_dygn
    name: Uur per dag
  - entity: sensor.pump_aktuellt_pris
    name: Huidige prijs
  - entity: sensor.pump_nasta_start
    name: Volgende start
  - entity: button.pump_pausa
    name: 🛁 Pauze voor het bad
  - entity: sensor.pump_sparade_kronor
    name: Bespaard vandaag
  - entity: sensor.pump_kostnad_idag
    name: Kosten vandaag
```

## Ondersteunde talen

English (en), Svenska (sv), Norsk (no), Suomi (fi), Dansk (da), Deutsch (de), Français (fr), Nederlands (nl)

## Licentie

MIT
