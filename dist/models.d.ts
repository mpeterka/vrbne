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
    date: string;
    time_from: string;
    time_to: string;
    note?: string;
    weather?: WeatherItem;
}
export declare class VrbneEventClass implements VrbneEvent {
    date: string;
    time_from: string;
    time_to: string;
    note: string;
    weather?: WeatherItem;
    tz: string;
    constructor(date: string, time_from: string, time_to: string, note: string | undefined, tz: string);
    private getDateTime;
    getDatetimeFrom(): DateTime;
    getDatetimeTo(): DateTime;
}
//# sourceMappingURL=models.d.ts.map