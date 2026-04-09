import axios from 'axios';
import { DateTime } from 'luxon';
import { WeatherItem, VrbneEvent } from './models.js';

const API_KEY = process.env.WEATHER_API_KEY;
const CITY_ID = '3077916'; // České Budějovice / Vrbné
const TZ = 'Europe/Prague';

export async function fetchWeather(): Promise<WeatherItem[]> {
  if (!API_KEY) {
    console.warn('[Weather] No API_KEY configured');
    return [];
  }

  try {
    console.log(`[Weather] Fetching forecast`);
    const response = await axios.get(
      `https://api.openweathermap.org/data/2.5/forecast?id=${CITY_ID}&APPID=${API_KEY}&lang=cz&units=metric`,
      { timeout: 10000 }
    );
    const data = response.data;

    const weatherList: WeatherItem[] = [];

    if (!data.list) {
      console.warn('[Weather] No forecast data in response');
      return [];
    }

    for (const item of data.list) {
      try {
        weatherList.push({
          date: DateTime.fromSeconds(item.dt, { zone: TZ }),
          feels_like: item.main.feels_like,
          temp: item.main.temp,
          wind_speed: item.wind.speed,
          icon: item.weather[0].icon,
          desc: item.weather[0].description,
        });
      } catch {
        // Skip invalid records
        continue;
      }
    }

    console.log(`[Weather] Successfully fetched ${weatherList.length} forecast entries`);
    return weatherList;
  } catch (error) {
    console.error('[Weather] Error fetching forecast:', error);
    return [];
  }
}

export function assignWeather(events: VrbneEvent[], weather: WeatherItem[]): void {
  for (const event of events) {
    const startDt = DateTime.fromISO(
      `${event.date}T${event.time_from}:00`,
      { zone: TZ }
    );
    const endDt = DateTime.fromISO(
      `${event.date}T${event.time_to}:00`,
      { zone: TZ }
    );

    // Find the closest forecast (OpenWeatherMap provides 3-hour steps)
    // We look for a forecast that is within 90 minutes of the event's start
    let closest: WeatherItem | null = null;
    let minDiffMinutes = Infinity;

    for (const w of weather) {
      const diffMinutes = Math.abs(w.date.diff(startDt, 'minutes').minutes);
      if (diffMinutes < minDiffMinutes) {
        minDiffMinutes = diffMinutes;
        closest = w;
      }
    }

    // Only assign if the forecast is reasonably close (e.g., within 2 hours of start)
    if (closest && minDiffMinutes <= 120) {
      event.weather = closest;
    } else {
      console.log(`[Weather] No close forecast found for event ${event.date} ${event.time_from} (min diff: ${minDiffMinutes === Infinity ? 'N/A' : Math.round(minDiffMinutes)}m)`);
    }
  }
}
