import datetime
import uuid
from typing import List

from handler_scrapper import URL
from handler_vrbne_event import VrbneEvent, WeatherItem
from icalendar import Calendar, Event


def get_description(event: VrbneEvent) -> str:
    desc = "(bez záruky…)\n" \
           + "• " + URL + "\n" \
           + "• " + "http://jakoubek.cz/usd " + "\n" \
           + "• " + "https://raftingcb.cz " + "\n" \
           + "• " + "https://www.slalom.cz "
    if event.weather is not None:
        w = event.weather
        desc += "\n\n" \
                + "Počasí (" + w.date.strftime("%H.%M") + ")\n" \
                + "🌡️ Teplota:  {:3.0f}".format(event.weather.temp) + " °C\n" \
                + "🌡️ Pocitová: {:3.0f}".format(event.weather.feels_like) + " °C\n" \
                + "🌬️ Vítr:     {:3.0f}".format(event.weather.wind_speed) + " m/s\n" \
                + "🐀 " + w.desc

    return desc


def get_summary(event: VrbneEvent) -> str:
    result = '🌊 Vrbné '
    if event.weather is not None:
        result += get_weather_icon(event.weather)
        result += "{:3.0f}".format(event.weather.feels_like) + "°C "
    if event.note:
        result += " !!! + " + event.note
    return result


def get_weather_icon(weather: WeatherItem) -> '':
    icons = {
        "01d": "☀",
        "02d": "⛅",
        "03d": "☁",
        "04d": "☁",
        "09d": "⛆",
        "10d": "🌧️",
        "11d": "⛈",
        "13d": "❄",
        "50d": "🌫️",
        "01n": "🌕",
        "02n": "🌤️",
        "03n": "☁",
        "04n": "☁☁",
        "09n": "🚿",
        "10n": "☔",
        "11n": "⛈",
        "13n": "❄",
        "50n": "🌁"
    }
    return icons.get(weather.icon, '')


# Se seznamu události vyrobí iCalendar (.ics) obsah
def ical(events: List[VrbneEvent]) -> str:
    cal = Calendar()
    cal.add('prodid', '-//vrbne-py')
    cal.add('version', '2.0')
    cal.add('name', "kanál České Vrbné")
    cal.add('description', "provoz slalomového kanálu")
    for event in events:
        cal_event = Event()
        cal_event.add("uid", uuid.uuid1().__str__() + "@vrbne-py")
        cal_event.add("dtstamp", datetime.datetime.now())
        cal_event.add("dtstart", event.datetime_from())
        cal_event.add("dtend", event.datetime_to())
        cal_event.add("summary", get_summary(event))
        cal_event.add("description", get_description(event))
        cal.add_component(cal_event)

    return cal.to_ical().decode("UTF-8")
