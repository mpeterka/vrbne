import datetime

import pytz

TZ = pytz.timezone("Europe/Prague")

class Weather:
    feels_like: float
    weather: str = ''

# Událost - vlastní pouštění vody
class VrbneEvent:
    # datum události
    date: datetime.date
    # čas kdy otevírají vodu
    timeFrom: str = ''
    # čas kdy zavírají vodu
    timeTo: str = ''
    # poznámka - nějaký tréning, závody apod.
    note: str = ''
    weather: Weather = None

    def __str__(self):
        return self.date.isoformat() + " " + self.timeFrom + "-" + self.timeTo + ", '" + self.note + "'"

    def datetime(self, time: str) -> datetime:
        result = datetime.datetime.now(TZ)
        time = time.split(":")
        result = result.replace(day=self.date.day, month=self.date.month, year=self.date.year)
        result = result.replace(hour=int(time[0]), minute=int(time[1]))
        result = result.replace(second=0, microsecond=0)
        return result

    def datetime_from(self) -> datetime:
        return self.datetime(self.timeFrom)

    def datetime_to(self) -> datetime:
        return self.datetime(self.timeTo)
