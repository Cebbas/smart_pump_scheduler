[🇬🇧 English](README.md) | [🇸🇪 Svenska](README.sv.md) | [🇳🇴 Norsk](README.no.md) | [🇫🇮 Suomi](README.fi.md) | [🇩🇰 Dansk](README.da.md) | **🇩🇪 Deutsch** | [🇫🇷 Français](README.fr.md) | [🇳🇱 Nederlands](README.nl.md)

---

# Pollen Pump 🌿

Eine Home Assistant-Integration (HACS), die die Laufzeiten Ihrer Pumpe basierend auf Strompreisen optimiert.

## Funktionen

- 🔌 **Flexible Preisquelle** – Nordpool (automatisch), beliebiger HA-Sensor (Tibber usw.) oder fester Zeitplan
- ⏰ **Intelligente Planung** – läuft in den N günstigsten Stunden pro Tag
- 📅 **Wochentagssteuerung** – verschiedene Stunden, Zeitfenster oder vollständige Deaktivierung pro Tag
- 🛁 **Pausenfunktion** – Pause zum Baden und automatische Neuplanung einer Ersatzstunde
- ⚡ **Energieverfolgung** – echter Sensor oder manuelle Watt-Einstellung, berechnet Kosten und Einsparungen
- 🌍 **Mehrsprachig** – folgt der Spracheinstellung von Home Assistant (DE, EN, SV, NO, FI, DA, FR, NL)
- 💰 **Preisgrenzen** – immer laufen unter X Ct, nie laufen über Y Ct

## Installation über HACS

1. Öffnen Sie HACS in Home Assistant
2. Gehen Sie zu **Integrationen** → Drei-Punkte-Menü → **Benutzerdefinierte Repositories**
3. Fügen Sie `https://github.com/your-username/pollen_pump` als **Integration** hinzu
4. Installieren Sie **Pollen Pump**
5. Starten Sie Home Assistant neu
6. Gehen Sie zu **Einstellungen → Geräte & Dienste → Integration hinzufügen → Pollen Pump**

## Konfiguration

Die Integration wird vollständig über die Benutzeroberfläche konfiguriert – keine YAML-Bearbeitung erforderlich.

### Schritt 1 – Preisquelle
| Option | Beschreibung |
|---|---|
| Nordpool | Ruft Preise automatisch ab. Wählen Sie Gebiet (DE, SE1–SE4, NO, DK, FI...) und Währung. |
| HA-Sensor | Verwenden Sie einen vorhandenen Sensor von Nordpool, Tibber oder einer anderen Integration. |
| Fester Zeitplan | Keine Preisoptimierung – läuft in einem festen Zeitfenster. |

### Schritt 2 – Pumpeneinstellungen
- Wählen Sie die Schalter-Entität, die Ihre Pumpe steuert
- Stunden pro Tag einstellen (1–24)
- Optional: immer laufen unter X Ct/kWh
- Optional: nie laufen über Y Ct/kWh

### Schritt 3 – Zeitplan
- Globales Zeitfenster (z.B. 06:00–22:00)
- Oder Wochentagseinstellungen mit individuellen Start/Stopp-Zeiten und Stunden aktivieren
- Bestimmte Tage vollständig deaktivieren

### Schritt 4 – Pauseneinstellungen
- Pausenfunktion aktivieren/deaktivieren
- Pausendauer festlegen (Standard 60 Min.)
- Max. Pausen pro Tag festlegen

### Schritt 5 – Energiemessung
- Energie/Leistungssensor von Ihrer Smart-Steckdose verbinden
- Oder den Leistungsverbrauch der Pumpe manuell in Watt eingeben
- Wird für Kosten- und Einsparungsberechnungen verwendet

## Erstellte Entitäten

| Entität | Beschreibung |
|---|---|
| `binary_sensor.pump_schema` | EIN wenn die Pumpe laufen soll |
| `sensor.pump_aktuellt_pris` | Aktueller Strompreis |
| `sensor.pump_nasta_start` | Nächster geplanter Start |
| `sensor.pump_timmar_kvar_idag` | Geplante Stunden verbleibend heute |
| `sensor.pump_energi_idag` | Verbrauchte Energie heute (kWh) |
| `sensor.pump_kostnad_idag` | Kosten heute |
| `sensor.pump_sparade_kronor` | Einsparung vs. Betrieb zu teuren Stunden |
| `sensor.pump_effekt` | Aktuelle Leistung |
| `switch.pump_paus` | Pause ein/aus schalten |
| `button.pump_pausa` | Pause für konfigurierte Dauer |
| `number.pump_timmar_per_dygn` | Tägliche Stunden vom Dashboard anpassen |

## Dienste

| Dienst | Beschreibung |
|---|---|
| `pollen_pump.pausa` | Pumpe für N Minuten pausieren |
| `pollen_pump.aterstall` | Pause abbrechen, zum Zeitplan zurückkehren |
| `pollen_pump.uppdatera_schema` | Neuberechnung des heutigen Zeitplans erzwingen |

## Dashboard-Karten-Beispiel

```yaml
type: entities
title: Pollenpumpe
entities:
  - entity: binary_sensor.pump_schema
    name: Läuft jetzt
  - entity: number.pump_timmar_per_dygn
    name: Stunden pro Tag
  - entity: sensor.pump_aktuellt_pris
    name: Aktueller Preis
  - entity: sensor.pump_nasta_start
    name: Nächster Start
  - entity: button.pump_pausa
    name: 🛁 Pause zum Baden
  - entity: sensor.pump_sparade_kronor
    name: Heute gespart
  - entity: sensor.pump_kostnad_idag
    name: Kosten heute
```

## Unterstützte Sprachen

English (en), Svenska (sv), Norsk (no), Suomi (fi), Dansk (da), Deutsch (de), Français (fr), Nederlands (nl)

## Lizenz

MIT
