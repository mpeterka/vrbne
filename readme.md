# Vrbné iCal Service

Tato služba poskytuje aktuální rozpis provozu slalomového kanálu v Českém Vrbném ve formátu iCalendar (`.ics`). Kalendář lze snadno importovat do Google Kalendáře, Microsoft Outlooku nebo Apple Calendar.

## Funkce
- **Automatické scrapování**: Data jsou automaticky stahována z oficiálního webu [itdev.cz](http://itdev.cz/SlalomCourse/OpeningTimes.aspx).
- **Předpověď počasí**: Možnost zahrnout informaci o počasí přímo do názvu a popisu události.
- **Caching**: Výstupy jsou cachovány na 1 hodinu, aby se šetřil zdrojový server.
- **Podpora Outlooku**: Obsahuje `VTIMEZONE` pro správné zobrazení času v MS Outlooku.
- **Docker**: Snadné nasazení pomocí Dockeru.

## Rychlý start (Docker)

1. Sestavte image:
   ```bash
   docker build -t vrbne-ical .
   ```

2. Spusťte kontejner:
   ```bash
   docker run -d -p 8000:8000 --name vrbne-app vrbne-ical
   ```

Aplikace bude dostupná na `https://karotka.peterka.name/vrbne`.

## Nasazení za Nginx Proxy
Pokud aplikaci provozujete za reverzní proxy (např. Nginx) pod jinou cestou než `/`, existují dvě hlavní možnosti, jak to vyřešit v závislosti na vaší Nginx konfiguraci.

### Možnost A: Ořezávání cesty v Nginx (Doporučeno pro vaši konfiguraci)
Pokud váš Nginx blok vypadá takto (s lomítkem na konci `proxy_pass` a `location`):

```nginx
location /vrbne/ {
    proxy_pass http://vrbne_backend/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

V tomto případě Nginx **ořeže** prefix `/vrbne/` a aplikace uvidí požadavky jako `/` nebo `/ical`.
**Nastavení Dockeru:** Aplikaci spusťte normálně bez parametru `--root-path`. Toto je nyní výchozí nastavení v `Dockerfile`.

### Možnost B: Ponechání cesty (Transparentní proxy)
Pokud váš Nginx blok vypadá takto (bez lomítka na konci):

```nginx
location /vrbne {
    proxy_pass http://vrbne_backend;
    ...
}
```

V tomto případě musí aplikace vědět, že běží pod prefixem.
**Nastavení Dockeru:** Přidejte parametr `--root-path /vrbne` do spouštěcího příkazu (nebo jej vraťte do `Dockerfile`).

> **Tip**: Pro správnou funkci automatické detekce protokolu (https) a adresy v dokumentaci ponechte v Nginxu hlavičky `X-Forwarded-Proto $scheme` a v uvicornu parametry `--proxy-headers --forwarded-allow-ips "*"`.

## API Endpointy

### `GET /ical`
Vrátí iCal soubor s rozpisem.
- **Parametry**:
  - `weather` (bool, default: `true`): Určuje, zda se má do kalendáře přidat předpověď počasí.
- **Příklad**: `https://karotka.peterka.name/vrbne/ical?weather=false`

### `GET /`
Zobrazí webovou stránku s návodem na přidání kalendáře do různých klientů.

## Konfigurace Počasí
Pro funkčnost počasí je nutné nastavit proměnnou prostředí `WEATHER_API_KEY` (z OpenWeatherMap). Pokud není nastavena, kalendář se vygeneruje bez informací o počasí.

```bash
docker run -d -p 8000:8000 -e WEATHER_API_KEY="vas_api_klic" vrbne-ical
```

## Vývoj a instalace bez Dockeru
1. Nainstalujte závislosti: `pip install -r requirements.txt`
2. Spusťte server: `python main.py`

## Dokumentace
Podrobnější návody pro konkrétní kalendáře naleznete v adresáři `/doc` nebo přímo na úvodní stránce běžící aplikace.
