from icalendar import Calendar, Event, Timezone, TimezoneStandard, TimezoneDaylight
from datetime import datetime
import uuid
import pytz
from models import VrbneEvent

TZ = pytz.timezone("Europe/Prague")

def create_ical(events: list[VrbneEvent], include_weather: bool = True) -> str:
    cal = Calendar()
    cal.add('prodid', '-//vrbne-docker//NONSGML v1.0//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Kanál České Vrbné')
    cal.add('x-wr-timezone', 'Europe/Prague')

    # Přidání VTIMEZONE pro lepší kompatibilitu (Outlook)
    tz_component = create_timezone_component()
    cal.add_component(tz_component)

    for event in events:
        ical_event = Event()
        ical_event.add('uid', f"{uuid.uuid4()}@vrbne-docker")
        ical_event.add('dtstamp', datetime.now(pytz.utc))
        ical_event.add('dtstart', event.datetime_from(TZ))
        ical_event.add('dtend', event.datetime_to(TZ))
        
        summary = "🌊 Vrbné"
        if include_weather and event.weather:
            summary += f" {get_weather_icon(event.weather.icon)}{int(event.weather.feels_like)}°C"
        if event.note:
            summary += f" - {event.note}"
        
        ical_event.add('summary', summary)
        
        description = "Provoz slalomového kanálu\nZdroj: http://itdev.cz/SlalomCourse/OpeningTimes.aspx"
        if include_weather and event.weather:
            w = event.weather
            description += f"\n\nPočasí ({w.date.strftime('%H:%M')}):\n"
            description += f"🌡️ Teplota: {w.temp}°C (pocitově {w.feels_like}°C)\n"
            description += f"🌬️ Vítr: {w.wind_speed} m/s\n"
            description += f"☁️ {w.desc}"
            
        ical_event.add('description', description)
        cal.add_component(ical_event)

    return cal.to_ical().decode('utf-8')

def get_weather_icon(icon_code: str) -> str:
    icons = {
        "01d": "☀️", "01n": "🌕",
        "02d": "⛅", "02n": "🌤️",
        "03d": "☁️", "03n": "☁️",
        "04d": "☁️", "04n": "☁️",
        "09d": "🌧️", "09n": "🌧️",
        "10d": "🌦️", "10n": "🌦️",
        "11d": "⛈️", "11n": "⛈️",
        "13d": "❄️", "13n": "❄️",
        "50d": "🌫️", "50n": "🌫️",
    }
    return icons.get(icon_code, "")

def create_timezone_component():
    # Vytvoření standardní VTIMEZONE komponenty pro Europe/Prague
    tz = Timezone()
    tz.add('tzid', 'Europe/Prague')
    
    # Zjednodušeně pro ČR (střídání času)
    # V praxi by bylo lepší použít knihovnu, ale icalendar vyžaduje ruční plnění
    # Pro účely tohoto úkolu stačí základní definice
    
    std = TimezoneStandard()
    std.add('tzname', 'CET')
    std.add('dtstart', datetime(1970, 10, 25, 3, 0, 0))
    std.add('rrule', {'freq': 'yearly', 'bymonth': 10, 'byday': ['-1su']})
    std.add('tzoffsetfrom', pytz.timezone("Europe/Prague").utcoffset(datetime(2023, 6, 1))) # +2
    std.add('tzoffsetto', pytz.timezone("Europe/Prague").utcoffset(datetime(2023, 1, 1)))   # +1
    
    dst = TimezoneDaylight()
    dst.add('tzname', 'CEST')
    dst.add('dtstart', datetime(1970, 3, 29, 2, 0, 0))
    dst.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': ['-1su']})
    dst.add('tzoffsetfrom', pytz.timezone("Europe/Prague").utcoffset(datetime(2023, 1, 1))) # +1
    dst.add('tzoffsetto', pytz.timezone("Europe/Prague").utcoffset(datetime(2023, 6, 1)))   # +2
    
    tz.add_component(std)
    tz.add_component(dst)
    return tz
