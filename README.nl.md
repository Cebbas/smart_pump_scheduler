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
- ▶️ **Nu starten** – draait op aanvraag voor een instelbare duur (bv. na het bad), wacht automatisch tot de prijs onder je maximumdrempel komt
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

## Handmatige installatie (zonder HACS)

1. Download deze repository als ZIP (**Code → Download ZIP** op GitHub, of een release-ZIP via de [releasespagina](https://github.com/Cebbas/smart_pump_scheduler/releases))
2. Kopieer de map `custom_components/smart_pump_scheduler` naar de map `config/custom_components/` van je Home Assistant, zodat je `config/custom_components/smart_pump_scheduler/manifest.json` krijgt
3. Herstart Home Assistant
4. Ga naar **Instellingen → Apparaten & diensten → Integratie toevoegen → Smart Pump Scheduler**

Je moet stap 1-3 handmatig herhalen bij toekomstige updates, omdat HACS dit normaal automatisch regelt.

## Configuratie

De integratie wordt volledig geconfigureerd via de gebruikersinterface – geen YAML-bewerking vereist.

### Stap 1 – Prijsbron

Je geeft de pomp ook eerst een naam (handig als je er meerdere instelt).

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

### Stap 4 – Pauze- en nu starten-instellingen
- Pauze-functie in-/uitschakelen
- Pauze-duur instellen (standaard 60 min)
- Max. pauzes per dag instellen
- Duur voor "Nu starten" instellen (standaard 30 min) – gebruikt door de gelijknamige knop/dienst

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
| `sensor.pump_scheduled_hours_today` | De geplande uren van vandaag, als tijdsbereiken |
| `sensor.pump_energi_idag` | Verbruikte energie vandaag (kWh) |
| `sensor.pump_drifttid_idag` | Werkelijke looptijd van de pomp vandaag (minuten, met een geformatteerd "h min"-attribuut) |
| `sensor.pump_kostnad_idag` | Kosten vandaag |
| `sensor.pump_sparade_kronor` | Besparing vs. draaien op dure uren |
| `sensor.pump_effekt` | Huidig vermogen |
| `switch.pump_paus` | Pauze aan/uit schakelen |
| `button.pump_pausa` | Pauzeer voor geconfigureerde duur |
| `button.pump_kor_nu` | Nu starten voor geconfigureerde duur (wacht als prijs boven maximum is) |
| `number.pump_timmar_per_dygn` | Dagelijkse uren aanpassen via dashboard |
| `number.pump_kor_nu_minuter` | Duur voor "Nu starten" aanpassen via dashboard |

## Diensten

| Dienst | Beschrijving |
|---|---|
| `smart_pump_scheduler.pausa` | Pomp N minuten pauzeren |
| `smart_pump_scheduler.aterstall` | Pauze annuleren, terug naar schema |
| `smart_pump_scheduler.uppdatera_schema` | Herberekening van het schema van vandaag forceren |
| `smart_pump_scheduler.kor_nu` | Nu starten voor N minuten (wacht als prijs boven maximum is) |

## Waarschuwingen & meldingen

| Situatie | Waar je het ziet |
|---|---|
| De vandaag gewenste uren passen niet binnen het tijdvenster/de prijslimieten | **Instellingen → Systeem → Reparaties** ("Niet alle uren konden worden ingepland") |
| Een "Nu starten"-verzoek staat in de wachtrij omdat de prijs boven het maximum is | **Instellingen → Systeem → Reparaties** ("Wacht op een lagere prijs om op aanvraag te draaien") |
| Een wachtend verzoek start daadwerkelijk zodra de prijs daalt | Een melding (belpictogram / companion-app) |

Beide reparatiewaarschuwingen verdwijnen automatisch zodra ze zijn opgelost.

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
  - entity: button.pump_kor_nu
    name: ▶️ Nu starten
  - entity: sensor.pump_sparade_kronor
    name: Bespaard vandaag
  - entity: sensor.pump_kostnad_idag
    name: Kosten vandaag
```

## Het schema van vandaag visualiseren

De integratie kan geen grafiek toevoegen aan zijn eigen pagina onder Apparaten & diensten — die pagina is vastgelegd door de Home Assistant-kern en toont alleen entiteiten en diagnostiek. Grafieken horen in plaats daarvan op een dashboard, waar je twee opties hebt:

### Optie A – Geen extra afhankelijkheden

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

### Optie B – Grafiek (vereist [apexcharts-card](https://github.com/RomRider/apexcharts-card) via HACS)

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

## Ondersteunde talen

English (en), Svenska (sv), Norsk (no), Suomi (fi), Dansk (da), Deutsch (de), Français (fr), Nederlands (nl)

## Licentie

MIT
