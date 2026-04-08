from fastapi import FastAPI, Response, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response as FastAPIResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
import markdown
import os
from datetime import datetime, timedelta
from cachetools import TTLCache
import scrapper
import weather
import ical_gen

app = FastAPI(title="Vrbné iCal Service", root_path="/vrbne")

# Security Middleware pro bezpečnostní hlavičky
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self' https:; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; img-src 'self' data:;"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# CORS politika - iCal endpointy by měly být přístupné, ale omezíme metody
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Inicializace šablon
templates = Jinja2Templates(directory="templates")

# Cache na 1 hodinu
cache = TTLCache(maxsize=10, ttl=3600)

# Cesta k dokumentaci
DOC_DIR = "doc"

@app.get("/ical")
async def get_ical(weather_enabled: bool = Query(True, alias="weather")):
    cache_key = f"ical_{weather_enabled}"
    if cache_key in cache:
        return Response(content=cache[cache_key], media_type="text/calendar")
    
    events = await scrapper.fetch_events()
    if weather_enabled:
        weather_data = await weather.fetch_weather()
        weather.assign_weather(events, weather_data)
    
    ical_content = ical_gen.create_ical(events, include_weather=weather_enabled)
    cache[cache_key] = ical_content
    
    return Response(
        content=ical_content,
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=vrbne.ics"}
    )

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Jednoduché vygenerování statické stránky z markdownů v /doc
    # Pro jednoduchost spojíme vše do jedné stránky
    content = ""
    files = ["readme.md", "google.md", "outlook.md"]
    
    for filename in files:
        path = os.path.join(DOC_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                md_content = f.read()
                # Oprava cest k obrázkům pro statické servírování
                # Používáme relativní cestu k aktuálnímu mountu, aby to fungovalo i za proxy
                md_content = md_content.replace("](", "](static/")
                html = markdown.markdown(md_content)
                content += f"<section>{html}</section><hr>"

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"content": content}
    )

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # SVG favicon s emoji vlny 🌊
    svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <text y=".9em" font-size="90">🌊</text>
    </svg>
    """
    return FastAPIResponse(content=svg, media_type="image/svg+xml")

# Servírování obrázků z /doc
app.mount("/static", StaticFiles(directory=DOC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
