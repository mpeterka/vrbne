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

  const url = `https://api.openweathermap.org/data/2.5/forecast?id=${CITY_ID}&APPID=***&lang=cz&units=metric`;

  try {
    console.log(`[Weather] Fetching forecast for city ${CITY_ID}`);
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
    // We need to convert event to VrbneEventClass if it's not already
    const startDt = DateTime.fromISO(
      `${event.date}T${event.time_from}:00`,
      { zone: TZ }
    );
    const endDt = DateTime.fromISO(
      `${event.date}T${event.time_to}:00`,
      { zone: TZ }
    );

    // Find the closest forecast that falls within the interval
    let found: WeatherItem | null = null;
    for (const w of weather) {
      if (w.date >= startDt && w.date <= endDt) {
        found = w;
        break;
      }
    }

    event.weather = found || undefined;
  }
}
