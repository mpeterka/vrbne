import json
import logging
import os
import urllib.request
from datetime import datetime
from typing import List, Optional

from handler_vrbne_event import VrbneEvent, TZ, WeatherItem

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# Downloads weather info
# Expected system environment WEATHER_API_KEY with API key for https://api.openweathermap.org
#


def set_weather(events: List[VrbneEvent]):
    if len(events) == 0:
        # no events, so no weather forecast is needed
        return
    weather = get_weather()
    for e in events:
        w = find_weather(e, weather)
        if w is not None:
            e.weather = w


def find_weather(event: VrbneEvent, weather: List[WeatherItem]) -> Optional[WeatherItem]:
    for w in weather:
        if event.datetime_from() <= w.date <= event.datetime_to():
            logger.debug("For " + event.__str__() + " found " + w.__str__() + " exactly.")
            return w
    # fallback = min(weather, key=lambda x: abs(x.date.date() - event.date))
    # return fallback
    return None


def get_weather() -> List[WeatherItem]:
    result = []
    weather_api_key = os.environ.get('WEATHER_API_KEY')
    if weather_api_key is not None:
        try:
            url = "https://api.openweathermap.org/data/2.5/forecast?id=3077916&APPID=" + weather_api_key + "&lang=cz&units=metric"
            logger.info("Loading {0}".format(url))
            response = urllib.request.urlopen(url).read()
            weather = json.loads(response.decode("utf-8"))
            for w in weather["list"]:
                wi = WeatherItem()
                wi.feels_like = w["main"]["feels_like"]
                wi.temp = w["main"]["temp"]
                wi.wind_speed = w["wind"]["speed"]
                wi.icon = w["weather"][0]["icon"]
                wi.desc = w["weather"][0]["description"]
                wi.date = datetime.fromtimestamp(w["dt"], tz=TZ)
                result.append(wi)
            return result
        except Exception:
            logger.exception("Failed to fetch weather")
            return result
    else:
        logger.warning("No WEATHER_API_KEY Found - skipping weather fetch.")
        return result


# Jen pro testy bez AWS
def main():
    logging.basicConfig(level=logging.DEBUG)
    weather = get_weather()
    for w in weather:
        print(w)

    print("now: ")
    event = VrbneEvent()
    event.date = datetime.now(TZ)
    event.timeFrom = "09:00"
    event.timeTo = "10:00"
    print(find_weather(event, weather))


if __name__ == '__main__':
    main()
