# Testa Smart Pump Scheduler lokalt

Steg-för-steg guide för att testa integrationen i din Home Assistant innan du pushar till GitHub.

---

## Alternativ 1 – Kopiera manuellt (enklast)

### Förutsättningar
- Home Assistant installerat (HassOS, Docker eller manuellt)
- Filåtkomst till HA:s konfigurationsmapp

### Steg

**1. Hitta din HA config-mapp**

Mappen innehåller bl.a. `configuration.yaml`. Vanliga platser:
- HassOS / HA OS: `/config/`
- Docker: Mappen du mountade som `/config`
- Manuell installation: `~/.homeassistant/`

**2. Skapa mappen om den inte finns**
```bash
mkdir -p /config/custom_components
```

**3. Kopiera integrationen**
```bash
cp -r custom_components/smart_pump_scheduler /config/custom_components/
```

**4. Starta om Home Assistant**

Inställningar → System → Starta om

**5. Lägg till integrationen**

Inställningar → Enheter & tjänster → Lägg till integration → sök "Smart Pump Scheduler"

---

## Alternativ 2 – Samba-tillägget (bäst för aktiv utveckling)

Med Samba kan VS Code spara direkt till HA utan att kopiera manuellt.

### Installera Samba i HA

1. Inställningar → Tillägg → Tilläggslager → sök **Samba share**
2. Installera och starta
3. Konfigurera användare/lösenord i tilläggets inställningar

### Montera i VS Code (macOS)

1. Finder → Gå → Anslut till server
2. Skriv: `smb://homeassistant.local/config`
3. Logga in med dina Samba-uppgifter

### Montera i VS Code (Windows)

1. Utforskaren → Denna dator → Anslut nätverksenhet
2. Skriv: `\\homeassistant.local\config`

### Skapa en symlink (macOS/Linux) – automatisk sync

```bash
# Ta bort befintlig mapp om den finns
rm -rf /Volumes/config/custom_components/smart_pump_scheduler

# Skapa symlink – ändringar i repot syns direkt i HA
ln -s $(pwd)/custom_components/smart_pump_scheduler /Volumes/config/custom_components/smart_pump_scheduler
```

Nu räcker det med att starta om HA efter varje ändring.

---

## Alternativ 3 – VS Code Remote SSH

Om HA kör på en Raspberry Pi eller annan server kan du jobba direkt på den.

1. Installera tillägget **Remote - SSH** i VS Code
2. Aktivera SSH i HA: Inställningar → Tillägg → **Advanced SSH & Web Terminal**
3. Anslut i VS Code: `Ctrl+Shift+P` → **Remote-SSH: Connect to Host**
4. Skriv: `root@homeassistant.local`
5. Öppna mappen `/config/custom_components/smart_pump_scheduler`

---

## Felsökning

### Integrationen syns inte i HA

- Kontrollera att mappen heter exakt `smart_pump_scheduler` (inga stora bokstäver)
- Kontrollera att `manifest.json` finns i mappen
- Starta om HA igen

### Fel i loggen

Gå till **Inställningar → System → Loggar** och filtrera på `smart_pump_scheduler`.

Eller via SSH:
```bash
grep smart_pump_scheduler /config/home-assistant.log
```

### Validera filerna lokalt innan du kopierar

```bash
# Kontrollera JSON
python3 -c "
import json, glob
for f in glob.glob('custom_components/smart_pump_scheduler/translations/*.json'):
    json.load(open(f))
    print(f'✅ {f}')
"

# Kontrollera Python
for f in custom_components/smart_pump_scheduler/*.py; do
    python3 -m py_compile "$f" && echo "✅ $f"
done
```

---

## Testchecklista

Gå igenom dessa punkter efter installation:

- [X] Integrationen syns i "Lägg till integration"
- [X] Config flow startar (steg 1 – priskälla visas)
- [X] Kan välja Nordpool + område + valuta
- [X] Kan välja pump-switch från dropdown
- [X] Schema-inställningar visas korrekt (tider per dag)
- [X] Pausinställningar visas
- [X] Energiinställningar visas
- [X] Integrationen sparas utan fel
- [X] Entiteter skapas (`binary_sensor`, sensorer, knapp, switch, number)
- [ ] `binary_sensor.pump_schema` uppdateras varje timme
- [ ] Pausknappen stänger av pumpen
- [ ] Pumpen startar igen efter paustidens slut
- [X] Rätt språk visas (testa genom att byta HA-språk)

---

## Tips för snabbare iteration

Istället för att starta om hela HA efter varje ändring kan du ladda om bara integrationen:

**Utvecklarverktyg → Tjänster → `homeassistant.reload_config_entry`**

Välj Smart Pump Scheduler-instansen → Anropa. Snabbare än full omstart!
