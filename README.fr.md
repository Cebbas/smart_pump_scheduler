<p align="center"><img src="logo.png" alt="Smart Pump Scheduler" width="420"></p>

[🇬🇧 English](README.md) | [🇸🇪 Svenska](README.sv.md) | [🇳🇴 Norsk](README.no.md) | [🇫🇮 Suomi](README.fi.md) | [🇩🇰 Dansk](README.da.md) | [🇩🇪 Deutsch](README.de.md) | **🇫🇷 Français** | [🇳🇱 Nederlands](README.nl.md)

---

# Smart Pump Scheduler

Une intégration Home Assistant (HACS) qui optimise les heures de fonctionnement de votre pompe en fonction des prix de l'électricité.

## Fonctionnalités

- 🔌 **Source de prix flexible** – Nordpool (automatique), n'importe quel capteur HA (Tibber, etc.) ou planning fixe
- ⏰ **Planification intelligente** – fonctionne pendant les N heures les moins chères par jour
- 📅 **Contrôle par jour de semaine** – heures différentes, fenêtres horaires ou désactivation complète par jour
- 🛁 **Fonction pause** – pause pour le bain et replanification automatique d'une heure de remplacement
- ⚡ **Suivi énergétique** – vrai capteur ou réglage manuel en watts, calcule le coût et les économies
- 🌍 **Multilingue** – suit le paramètre de langue de Home Assistant (FR, EN, SV, NO, FI, DA, DE, NL)
- 💰 **Limites de prix** – toujours actif sous X c, jamais actif au-dessus de Y c

## Installation via HACS

1. Ouvrez HACS dans Home Assistant
2. Allez dans **Intégrations** → menu trois points → **Dépôts personnalisés**
3. Ajoutez `https://github.com/Cebbas/smart_pump_scheduler` comme **Intégration**
4. Installez **Smart Pump Scheduler**
5. Redémarrez Home Assistant
6. Allez dans **Paramètres → Appareils & services → Ajouter une intégration → Smart Pump Scheduler**

## Installation manuelle (sans HACS)

1. Téléchargez ce dépôt en ZIP (**Code → Download ZIP** sur GitHub, ou un ZIP de release depuis la [page des releases](https://github.com/Cebbas/smart_pump_scheduler/releases))
2. Copiez le dossier `custom_components/smart_pump_scheduler` dans le dossier `config/custom_components/` de votre Home Assistant, afin d'obtenir `config/custom_components/smart_pump_scheduler/manifest.json`
3. Redémarrez Home Assistant
4. Allez dans **Paramètres → Appareils & services → Ajouter une intégration → Smart Pump Scheduler**

Vous devrez répéter les étapes 1 à 3 manuellement pour les futures mises à jour, car HACS s'en occupe normalement automatiquement.

## Configuration

L'intégration est entièrement configurée via l'interface – aucune modification YAML requise.

### Étape 1 – Source de prix

Vous donnez aussi d'abord un nom à la pompe (utile si vous en configurez plusieurs).

| Option | Description |
|---|---|
| Nordpool | Récupère les prix automatiquement. Choisissez la zone (FR, SE1–SE4, NO, DK, FI...) et la devise. |
| Capteur HA | Utilisez un capteur existant de Nordpool, Tibber ou toute autre intégration. |
| Planning fixe | Pas d'optimisation des prix – fonctionne sur une fenêtre horaire fixe. |

### Étape 2 – Paramètres de la pompe
- Sélectionnez l'entité switch contrôlant votre pompe
- Définissez les heures par jour (1–24)
- Optionnel : toujours actif sous X c/kWh
- Optionnel : jamais actif au-dessus de Y c/kWh

### Étape 3 – Planning
- Fenêtre horaire globale (ex. 06:00–22:00)
- Ou activez les paramètres par jour de semaine avec des heures de début/fin individuelles
- Désactivez des jours spécifiques entièrement

### Étape 4 – Paramètres de pause
- Activer/désactiver la fonction pause
- Définir la durée de pause (défaut 60 min)
- Définir le nombre max de pauses par jour

### Étape 5 – Suivi énergétique
- Connectez un capteur énergie/puissance de votre prise intelligente
- Ou entrez manuellement la consommation de la pompe en watts
- Utilisé pour les calculs de coût et d'économies

## Entités créées

| Entité | Description |
|---|---|
| `binary_sensor.pump_schema` | ALLUMÉ quand la pompe doit fonctionner |
| `sensor.pump_aktuellt_pris` | Prix électricité actuel |
| `sensor.pump_nasta_start` | Prochain démarrage planifié |
| `sensor.pump_timmar_kvar_idag` | Heures planifiées restantes aujourd'hui |
| `sensor.pump_scheduled_hours_today` | Les heures programmées du jour, sous forme de plages horaires |
| `sensor.pump_energi_idag` | Énergie consommée aujourd'hui (kWh) |
| `sensor.pump_kostnad_idag` | Coût aujourd'hui |
| `sensor.pump_sparade_kronor` | Économies vs fonctionnement aux heures chères |
| `sensor.pump_effekt` | Puissance actuelle |
| `switch.pump_paus` | Basculer la pause on/off |
| `button.pump_pausa` | Pause pour la durée configurée |
| `number.pump_timmar_per_dygn` | Ajuster les heures quotidiennes depuis le tableau de bord |

## Services

| Service | Description |
|---|---|
| `smart_pump_scheduler.pausa` | Mettre la pompe en pause N minutes |
| `smart_pump_scheduler.aterstall` | Annuler la pause, retour au planning |
| `smart_pump_scheduler.uppdatera_schema` | Forcer le recalcul du planning du jour |

## Exemple de carte tableau de bord

```yaml
type: entities
title: Planificateur de pompe intelligent
entities:
  - entity: binary_sensor.pump_schema
    name: Fonctionne maintenant
  - entity: number.pump_timmar_per_dygn
    name: Heures par jour
  - entity: sensor.pump_aktuellt_pris
    name: Prix actuel
  - entity: sensor.pump_nasta_start
    name: Prochain démarrage
  - entity: button.pump_pausa
    name: 🛁 Pause pour le bain
  - entity: sensor.pump_sparade_kronor
    name: Économisé aujourd'hui
  - entity: sensor.pump_kostnad_idag
    name: Coût aujourd'hui
```

## Visualiser le planning du jour

L'intégration ne peut pas ajouter de graphique à sa propre page Appareils & services — cette page est fixée par le cœur de Home Assistant et n'affiche que les entités et les diagnostics. Les graphiques ont plutôt leur place sur un tableau de bord, où vous avez deux options :

### Option A – Aucune dépendance supplémentaire

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

### Option B – Graphique (nécessite [apexcharts-card](https://github.com/RomRider/apexcharts-card) depuis HACS)

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

## Langues supportées

English (en), Svenska (sv), Norsk (no), Suomi (fi), Dansk (da), Deutsch (de), Français (fr), Nederlands (nl)

## Licence

MIT
