import os
import httpx
from datetime import datetime
from typing import List, Optional
import pytz
from models import WeatherItem, VrbneEvent

API_KEY = os.environ.get('WEATHER_API_KEY')
CITY_ID = "3077916" # České Budějovice / Vrbné
TZ = pytz.timezone("Europe/Prague")

async def fetch_weather() -> List[WeatherItem]:
    if not API_KEY:
        return []
        
    url = f"https://api.openweathermap.org/data/2.5/forecast?id={CITY_ID}&APPID={API_KEY}&lang=cz&units=metric"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            weather_list = []
            if "list" not in data:
                return []
                
            for item in data.get("list", []):
                try:
                    weather_list.append(WeatherItem(
                        date=datetime.fromtimestamp(item["dt"], tz=TZ),
                        feels_like=item["main"]["feels_like"],
                        temp=item["main"]["temp"],
                        wind_speed=item["wind"]["speed"],
                        icon=item["weather"][0]["icon"],
                        desc=item["weather"][0]["description"]
                    ))
                except (KeyError, IndexError, TypeError):
                    continue # Přeskočit neplatné záznamy
            return weather_list
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return []

def assign_weather(events: List[VrbneEvent], weather: List[WeatherItem]):
    for event in events:
        start = event.datetime_from(TZ)
        end = event.datetime_to(TZ)
        
        # Najdeme nejbližší předpověď, která spadá do intervalu
        found = None
        for w in weather:
            if start <= w.date <= end:
                found = w
                break
        
        event.weather = found
