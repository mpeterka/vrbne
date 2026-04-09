import { DateTime } from 'luxon';

export interface WeatherItem {
  date: DateTime;
  feels_like: number;
  temp: number;
  icon: string;
  desc: string;
  wind_speed: number;
}

export interface VrbneEvent {
  date: string; // YYYY-MM-DD format
  time_from: string; // HH:MM format
  time_to: string; // HH:MM format
  note?: string;
  weather?: WeatherItem;
}

export class VrbneEventClass implements VrbneEvent {
  date: string;
  time_from: string;
  time_to: string;
  note: string;
  weather?: WeatherItem;
  tz: string;

  constructor(date: string, time_from: string, time_to: string, note: string = '', tz: string) {
    this.date = date;
    this.time_from = time_from;
    this.time_to = time_to;
    this.note = note;
    this.tz = tz;
  }

  private getDateTime(timeStr: string): DateTime {
    const [h, m] = timeStr.split(':').map(Number);
    const [year, month, day] = this.date.split('-').map(Number);
    return DateTime.fromObject(
      { year, month, day, hour: h, minute: m },
      { zone: this.tz }
    );
  }

  getDatetimeFrom(): DateTime {
    return this.getDateTime(this.time_from);
  }

  getDatetimeTo(): DateTime {
    return this.getDateTime(this.time_to);
  }
}
