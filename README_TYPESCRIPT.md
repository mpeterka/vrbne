# Vrbné iCal Service - TypeScript Version

Projekt přepsaný z Pythonu do TypeScriptu s Express.js serverem.

## Instalace

### Lokální vývoj

```bash
# Nainstaluj dependencies
npm install

# Vytvořit .env soubor a přidat WEATHER_API_KEY
cp .env.example .env
# Edituj .env a přidej svůj OpenWeatherMap API klíč

# Vývoj (s hot reload)
npm run dev

# Build pro produkci
npm run build

# Start produkce
npm start
```

Server běží na `http://localhost:8000`

### Docker

```bash
# Builduj image
docker build -t vrbne-app .

# Spuštění s docker-compose (s nginx proxy)
docker-compose up -d

# Spuštění bez nginx (jen aplikace)
docker run -d \
  -p 8000:8000 \
  -e WEATHER_API_KEY=your_api_key \
  vrbne-app
```

## Endpointy

- `GET /` - Hlavní stránka s dokumentací
- `GET /ical` - iCal kalendář (s počasím)
- `GET /ical?weather=false` - iCal bez počasí
- `GET /favicon.ico` - Favicon

## Proxy konfigurace (nginx)

Aplikace správně podporuje proxy přesměrování pomocí `X-Forwarded-*` headerů:

- `X-Forwarded-For` - Client IP
- `X-Forwarded-Proto` - HTTP/HTTPS
- `X-Forwarded-Host` - Hostname

nginx.conf automaticky nastavuje tyto headery.

## Caching

Kalendář je cachován na **1 hodinu** (3600 sekund) a automaticky se obnovuje.

## Závislosti

### Production
- **express** - Web framework
- **axios** - HTTP client
- **cheerio** - Web scraping
- **ical-generator** - iCal generation
- **luxon** - Date/time handling
- **node-cache** - Simple caching
- **markdown-it** - Markdown parsing
- **ejs** - Template engine
- **cors** - CORS middleware
- **helmet** - Security headers
- **uuid** - UUID generation

### Development
- **typescript** - TypeScript compiler
- **ts-node** - TypeScript runner
- **nodemon** - Auto-reload
- **@types/* - Type definitions

## Migrované soubory

| Python | TypeScript |
|--------|-----------|
| models.py | src/models.ts |
| scrapper.py | src/scrapper.ts |
| weather.py | src/weather.ts |
| ical_gen.py | src/ical_gen.ts |
| main.py | src/main.ts |
| requirements.txt | package.json |

## Poznámky

- Projekt nyní používá **Luxon** místo pytz pro zpracování časových zón
- EJS template engine nahradil Jinja2
- Node.js Cache nahradil cachetools
- Bezpečnostní headery jsou nastaveny přes Helmet middleware
