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
Pokud aplikaci provozujete za reverzní proxy (např. Nginx) pod jinou cestou než `/`, je v `main.py` nastaveno `root_path="/vrbne"`. V Nginxu je potřeba předávat hlavičky pro správnou detekci HTTPS:

```nginx
location /vrbne/ {
    proxy_pass http://localhost:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## API Endpointy

### `GET /vrbne/ical`
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
