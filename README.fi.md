[🇬🇧 English](README.md) | [🇸🇪 Svenska](README.sv.md) | [🇳🇴 Norsk](README.no.md) | **🇫🇮 Suomi** | [🇩🇰 Dansk](README.da.md) | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | [🇳🇱 Nederlands](README.nl.md)

---

# Smart Pump Scheduler 🌿

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

## Konfigurointi

Integraatio konfiguroidaan kokonaan käyttöliittymän kautta – YAML-muokkausta ei tarvita.

### Vaihe 1 – Hintalähde
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
| `sensor.pump_energi_idag` | Kulutettu energia tänään (kWh) |
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

## Tuetut kielet

English (en), Svenska (sv), Norsk (no), Suomi (fi), Dansk (da), Deutsch (de), Français (fr), Nederlands (nl)

## Lisenssi

MIT
