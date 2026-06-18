<p align="center"><img src="logo.png" alt="Smart Pump Scheduler" width="420"></p>

[🇬🇧 English](README.md) | [🇸🇪 Svenska](README.sv.md) | [🇳🇴 Norsk](README.no.md) | **🇫🇮 Suomi** | [🇩🇰 Dansk](README.da.md) | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | [🇳🇱 Nederlands](README.nl.md)

---

# Smart Pump Scheduler

Home Assistant -integraatio (HACS), joka optimoi pumpun käyntiajat sähköhintojen perusteella.

## Ominaisuudet

- 🔌 **Joustava hintalähde** – Nordpool (automaattinen), mikä tahansa HA-anturi (Tibber jne.) tai kiinteä aikataulu
- ⏰ **Älykäs aikataulutus** – käynnistyy N halvimman tunnin aikana vuorokaudessa
- 📅 **Viikonpäiväkohtainen ohjaus** – eri tunnit, aikaikkuna tai poista käytöstä kokonaan päiväkohtaisesti
- 🛁 **Taukotoiminto** – tauko kylpemistä varten ja automaattinen korvausajan aikataulutus
- ⚡ **Energian seuranta** – oikea anturi tai manuaalinen watti-asetus, laskee kustannukset ja säästöt
- 🌍 **Monikielinen** – seuraa Home Assistantin kieliasetusta (FI, EN, SV, NO, DA, DE, FR, NL)
- 💰 **Hintarajat** – käy aina alle X snt, ei koskaan yli Y snt

## Asennus HACS:n kautta

1. Avaa HACS Home Assistantissa
2. Siirry kohtaan **Integraatiot** → kolmen pisteen valikko → **Mukautetut arkistot**
3. Lisää `https://github.com/Cebbas/smart_pump_scheduler` **Integraationa**
4. Asenna **Smart Pump Scheduler**
5. Käynnistä Home Assistant uudelleen
6. Siirry kohtaan **Asetukset → Laitteet ja palvelut → Lisää integraatio → Smart Pump Scheduler**

## Manuaalinen asennus (ilman HACS:ia)

1. Lataa tämä repo ZIP-tiedostona (**Code → Download ZIP** GitHubissa, tai julkaisun ZIP [julkaisusivulta](https://github.com/Cebbas/smart_pump_scheduler/releases))
2. Kopioi `custom_components/smart_pump_scheduler`-kansio Home Assistantin `config/custom_components/`-kansioon, niin että saat `config/custom_components/smart_pump_scheduler/manifest.json`
3. Käynnistä Home Assistant uudelleen
4. Siirry kohtaan **Asetukset → Laitteet ja palvelut → Lisää integraatio → Smart Pump Scheduler**

Sinun täytyy toistaa vaiheet 1–3 manuaalisesti tulevia päivityksiä varten, koska HACS hoitaa sen normaalisti automaattisesti.

## Konfigurointi

Integraatio konfiguroidaan kokonaan käyttöliittymän kautta – YAML-muokkausta ei tarvita.

### Vaihe 1 – Hintalähde

Annat pumpulle myös nimen ensin (hyödyllistä, jos asetat useamman kuin yhden).

| Vaihtoehto | Kuvaus |
|---|---|
| Nordpool | Hakee hinnat automaattisesti. Valitse alue (FI, SE1–SE4, NO, DK...) ja valuutta. |
| HA-anturi | Käytä olemassa olevaa anturia Nordpoolista, Tibberistä tai muusta integraatiosta. |
| Kiinteä aikataulu | Ei hintaoptimointia – toimii kiinteässä aikaikkunnassa. |

### Vaihe 2 – Pumppuasetukset
- Valitse pumpun ohjaava kytkinentiteetti
- Aseta tuntimäärä vuorokaudessa (1–24)
- Valinnainen: käy aina alle X snt/kWh
- Valinnainen: ei koskaan yli Y snt/kWh

### Vaihe 3 – Aikataulu
- Globaali aikaikkuna (esim. 06:00–22:00)
- Tai ota käyttöön viikonpäiväkohtaiset asetukset yksilöllisillä alku/loppu-ajoilla ja tunneilla
- Poista tietyt päivät kokonaan käytöstä

### Vaihe 4 – Taukoasetukset
- Ota taukotoiminto käyttöön / poista käytöstä
- Aseta tauon kesto (oletus 60 min)
- Aseta enimmäistaukojen määrä vuorokaudessa

### Vaihe 5 – Energiamittaus
- Kytke energia/tehoanturi älypistorasiasta
- Tai syötä pumpun tehonkulutus manuaalisesti watteina
- Käytetään kustannus- ja säästölaskelmiin

## Luodut entiteetit

| Entiteetti | Kuvaus |
|---|---|
| `binary_sensor.pump_schema` | PÄÄLLÄ kun pumpun tulee käynnistyä |
| `sensor.pump_aktuellt_pris` | Nykyinen sähköhinta |
| `sensor.pump_nasta_start` | Seuraava aikataulutettu käynnistys |
| `sensor.pump_timmar_kvar_idag` | Aikataulutettuja tunteja jäljellä tänään |
| `sensor.pump_scheduled_hours_today` | Tämän päivän ajastetut tunnit aikaväleinä |
| `sensor.pump_energi_idag` | Kulutettu energia tänään (kWh) |
| `sensor.pump_drifttid_idag` | Pumpun todellinen käyntiaika tänään |
| `sensor.pump_kostnad_idag` | Kustannus tänään |
| `sensor.pump_sparade_kronor` | Säästö vs. kalleimpina tunteina ajo |
| `sensor.pump_effekt` | Nykyinen teho |
| `switch.pump_paus` | Vaihda tauko päälle/pois |
| `button.pump_pausa` | Tauko konfiguroituun aikaan |
| `number.pump_timmar_per_dygn` | Säädä päivittäisiä tunteja kojelaudasta |

## Palvelut

| Palvelu | Kuvaus |
|---|---|
| `smart_pump_scheduler.pausa` | Keskeytä pumppu N minuutiksi |
| `smart_pump_scheduler.aterstall` | Peruuta tauko, palaa aikatauluun |
| `smart_pump_scheduler.uppdatera_schema` | Pakota tämän päivän aikataulun uudelleenlaskenta |

## Kojelauta-korttiesimerkki

```yaml
type: entities
title: Älykäs pumppuajastin
entities:
  - entity: binary_sensor.pump_schema
    name: Käynnissä nyt
  - entity: number.pump_timmar_per_dygn
    name: Tuntia vuorokaudessa
  - entity: sensor.pump_aktuellt_pris
    name: Nykyinen hinta
  - entity: sensor.pump_nasta_start
    name: Seuraava käynnistys
  - entity: button.pump_pausa
    name: 🛁 Tauko kylpemistä varten
  - entity: sensor.pump_sparade_kronor
    name: Säästetty tänään
  - entity: sensor.pump_kostnad_idag
    name: Kustannus tänään
```

## Tämän päivän aikataulun visualisointi

Integraatio ei voi lisätä kaaviota omalle Laitteet ja palvelut -sivulleen — kyseinen sivu on Home Assistantin ydintoiminnallisuuden lukitsema ja näyttää vain entiteetit ja diagnostiikan. Kaaviot kuuluvat sen sijaan kojelaudalle, jossa on kaksi vaihtoehtoa:

### Vaihtoehto A – Ei lisäriippuvuuksia

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

### Vaihtoehto B – Kaavio (vaatii [apexcharts-card](https://github.com/RomRider/apexcharts-card) HACS:sta)

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

## Tuetut kielet

English (en), Svenska (sv), Norsk (no), Suomi (fi), Dansk (da), Deutsch (de), Français (fr), Nederlands (nl)

## Lisenssi

MIT
