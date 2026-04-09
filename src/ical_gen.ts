import crypto from 'crypto';
import IcalGenerator from 'ical-generator';
import { DateTime } from 'luxon';
import { VrbneEvent } from './models.js';
import * as scrapper from './scrapper.js';
import * as weather from './weather.js';
import { fileURLToPath } from 'url';

const TZ = 'Europe/Prague';

export function createIcal(events: VrbneEvent[], includeWeather: boolean = true): string {
  const cal = new (IcalGenerator as any)({
    prodId: '-//vrbne-docker//NONSGML v1.0//EN',
    name: 'Kanál České Vrbné',
    timezone: TZ,
  });

  for (const event of events) {
    let summary = '🌊 Vrbné';

    if (includeWeather && event.weather) {
      const weatherIcon = getWeatherIcon(event.weather.icon);
      summary += ` ${weatherIcon}${Math.round(event.weather.feels_like)}°C`;
    }

    if (event.note) {
      summary += ` - ${event.note}`;
    }

    const startDt = DateTime.fromISO(
      `${event.date}T${event.time_from}:00`,
      { zone: TZ }
    );
    const endDt = DateTime.fromISO(
      `${event.date}T${event.time_to}:00`,
      { zone: TZ }
    );

    let description = 'Provoz slalomového kanálu\nZdroj: http://itdev.cz/SlalomCourse/OpeningTimes.aspx';

    if (includeWeather && event.weather) {
      const w = event.weather;
      description += `\n\nPočasí (${w.date.toFormat('HH:mm')}):\n`;
      description += `🌡️ Teplota: ${w.temp}°C (pocitově ${w.feels_like}°C)\n`;
      description += `🌬️ Vítr: ${w.wind_speed} m/s\n`;
      description += `☁️ ${w.desc}`;
    }

    // Generate a deterministic ID based on date and time
    const eventIdSource = `${event.date}-${event.time_from}-${event.time_to}`;
    const eventId = crypto.createHash('sha1').update(eventIdSource).digest('hex');

    const eventObj = cal.createEvent({
      id: eventId,
      summary,
      description,
      start: startDt.toJSDate(),
      end: endDt.toJSDate(),
      timezone: TZ,
      // Use the start date of the event as the timestamp (DTSTAMP)
      // to avoid triggering updates in calendar apps just because the generation time changed.
      timestamp: startDt.toUTC().toJSDate(),
    });
    eventObj.timezone(TZ);
  }

  return cal.toString().replace(/\r\n/g, '\n');
}

function getWeatherIcon(iconCode: string): string {
  const icons: Record<string, string> = {
    '01d': '☀️',
    '01n': '🌕',
    '02d': '⛅',
    '02n': '🌤️',
    '03d': '☁️',
    '03n': '☁️',
    '04d': '☁️',
    '04n': '☁️',
    '09d': '🌧️',
    '09n': '🌧️',
    '10d': '🌦️',
    '10n': '🌦️',
    '11d': '⛈️',
    '11n': '⛈️',
    '13d': '❄️',
    '13n': '❄️',
    '50d': '🌫️',
    '50n': '🌫️',
  };

  return icons[iconCode] || '';
}

async function main() {
  try {
    const events = await scrapper.fetchEvents();
    const weatherData = await weather.fetchWeather();
    weather.assignWeather(events, weatherData);
    const ical = createIcal(events, true);
    console.log(ical);
  } catch (error) {
    console.error('Error in main:', error);
  }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main();
}
