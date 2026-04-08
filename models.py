from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel

class WeatherItem(BaseModel):
    date: datetime
    feels_like: float
    temp: float
    icon: str = ''
    desc: str = ''
    wind_speed: float

class VrbneEvent(BaseModel):
    date: date
    time_from: str
    time_to: str
    note: str = ''
    weather: Optional[WeatherItem] = None

    def get_datetime(self, time_str: str, tz) -> datetime:
        # Původní logika byla trochu nešťastná, zkusíme to lépe
        h, m = map(int, time_str.split(':'))
        dt = datetime(self.date.year, self.date.month, self.date.day, h, m)
        return tz.localize(dt)

    def datetime_from(self, tz) -> datetime:
        return self.get_datetime(self.time_from, tz)

    def datetime_to(self, tz) -> datetime:
        return self.get_datetime(self.time_to, tz)
