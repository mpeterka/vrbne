import datetime
import uuid
from typing import List

from handler_scrapper import URL
from handler_vrbne_event import VrbneEvent, WeatherItem
from icalendar import Calendar, Event


def get_description(event: VrbneEvent) -> str:
    desc = "* " + URL + "\n" \
           + "* " + "http://jakoubek.cz/usd " + "\n" \
           + "* " + "https://raftingcb.cz/ " + "\n" \
           + "* " + "https://www.slalom.cz/ "
    if event.weather is not None:
        w = event.weather
        desc += "\n\n" \
                + "temp: {:3.0f}".format(event.weather.temp) + "°C\n" \
                + "feels-like: {:3.0f}".format(event.weather.feels_like) + "°C\n" \
                + w.weather_desc

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
        'Thunderstorm': '🌩️',
        'Drizzle': '☔',
        'Rain': '🌧️',
        'Snow': '❄',
        'Clouds': '☁',
        'Clear': '🌞',
    }
    return icons.get(weather.weather, '')


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
