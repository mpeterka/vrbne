FROM python:3.11-slim

WORKDIR /app

# Závislosti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Zdrojový kód
COPY . .

# Výchozí port pro FastAPI
EXPOSE 8000

# Proměnné prostředí
ENV WEATHER_API_KEY=""
ENV PYTHONUNBUFFERED=1

# Nainstalovat curl pro healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Zdravotní kontrola (Healthcheck)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Použití neprivilegovaného uživatele pro bezpečnost
RUN useradd -m vrbneuser && chown -R vrbneuser:vrbneuser /app
USER vrbneuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
