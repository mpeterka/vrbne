import datetime
import uuid
from typing import List

from handler_vrbne_event import VrbneEvent, Weather
from handler_scrapper import URL
from icalendar import Calendar, Event


def get_summary(event: VrbneEvent) -> str:
    result = '🌊 Vrbné '
    if event.weather is not None:
        result += get_weather_icon(event.weather)
        result += "{:3.0f}".format(event.weather.feels_like) + "°C "
    if event.note:
        result += " !!! + " + event.note
    return result

def get_weather_icon(weather: Weather) -> '':
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
        cal_event.add("description", URL)
        cal.add_component(cal_event)

    return cal.to_ical().decode("UTF-8")
