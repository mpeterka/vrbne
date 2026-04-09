import axios from 'axios';
import { DateTime } from 'luxon';
const API_KEY = process.env.WEATHER_API_KEY;
const CITY_ID = '3077916'; // České Budějovice / Vrbné
const TZ = 'Europe/Prague';
export async function fetchWeather() {
    if (!API_KEY) {
        return [];
    }
    const url = `https://api.openweathermap.org/data/2.5/forecast?id=${CITY_ID}&APPID=${API_KEY}&lang=cz&units=metric`;
    try {
        const response = await axios.get(url, { timeout: 10000 });
        const data = response.data;
        const weatherList = [];
        if (!data.list) {
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
            }
            catch {
                // Skip invalid records
                continue;
            }
        }
        return weatherList;
    }
    catch (error) {
        console.error('Error fetching weather:', error);
        return [];
    }
}
export function assignWeather(events, weather) {
    for (const event of events) {
        // We need to convert event to VrbneEventClass if it's not already
        const startDt = DateTime.fromISO(`${event.date}T${event.time_from}:00`, { zone: TZ });
        const endDt = DateTime.fromISO(`${event.date}T${event.time_to}:00`, { zone: TZ });
        // Find the closest forecast that falls within the interval
        let found = null;
        for (const w of weather) {
            if (w.date >= startDt && w.date <= endDt) {
                found = w;
                break;
            }
        }
        event.weather = found || undefined;
    }
}
//# sourceMappingURL=weather.js.map