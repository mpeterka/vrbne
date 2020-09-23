import datetime
import logging
import re
import urllib.request
import uuid
from typing import List, Tuple, Optional

import pytz
from bs4 import BeautifulSoup, ResultSet, Tag
from icalendar import Calendar, Event

#
# Stahuje z http://itdev.cz/SlalomCourse/OpeningTimes.aspx a vyrábí z něho icalendar pro import do kalendáře
#

URL = "http://itdev.cz/SlalomCourse/OpeningTimes.aspx"
TZ = pytz.timezone("Europe/Prague")


# AWS Lambda entrypoint
def icalendar(event, context):
    events = get_events()

    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/calendar"
        },
        "body": ical(events)
    }

    return response


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

    def __str__(self):
        return self.date.isoformat() + " " + self.timeFrom + "-" + self.timeTo + ", " + self.note

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


# Parsuje HTML a sestavuje z něho z seznam událostí
def get_events() -> List[VrbneEvent]:
    logging.info("Loading {0}".format(URL))
    html = urllib.request.urlopen(URL).read().decode("utf-8")
    soup = BeautifulSoup(html, features='html.parser')
    table = soup.find("table", class_="rgMasterTable")
    table_bodies = table.select("tbody")
    tbody = table_bodies[-1]
    rows = tbody.select("tr")
    return get_events_from_rows(rows)


# Nalezne události v celé řádce
def get_events_from_row(row: Tag) -> List[VrbneEvent]:
    events = []
    # noinspection PyBroadException
    try:
        date = get_first_content(row, "label")
        if date is None:
            pass  # asi prázdný řádek
        note = get_first_content(row, "td[align=left]")
        hours = get_hours(row.select("td[align=center]"))
        for i in range(len(hours)):
            event = VrbneEvent()
            event.date = get_date(date)
            # v jedné řádce jsou až dva časové intervaly
            hour = hours[i]
            event.timeFrom = hour[0]
            event.timeTo = hour[1]
            event.note = note
            events.append(event)
    except Exception:
        logging.exception("Nepodařilo se načíst řádek")
        pass
    return events


def get_events_from_rows(rows: ResultSet) -> List[VrbneEvent]:
    events = []
    for row in rows:
        events.extend(get_events_from_row(row))
    return events


# V řádce je jeden až dva časové intervaly - udělá s toho seznam
def get_hours(cells) -> List[Tuple[str, str]]:
    hours = []
    # naplnění seznamu, ořezané
    for cell in cells:
        hours.append(cell.text.strip())
    # odstranit data bez časů
    hours = list(filter(lambda hour: hour != '', hours))
    # pouze dopolední nebo odpolední pouštění
    if len(hours) == 2:
        return [(hours[0], hours[1])]
    # pouští dvakrát denně (4 časy)
    if len(hours) == 4:
        return [(hours[0], hours[1]), (hours[2], hours[3])]
    # nepouští, nebo není ještě vyplněno
    return []


# Z řetězce "dd.mm." vyrobí datum
def get_date(day_month: Optional[str]) -> Tuple[str]:
    year = datetime.date.today().year
    m = re.search('([0-9]{1,2})\\.([0-9]{1,2})\\.', day_month)
    month = m.group(2)
    day = m.group(1)
    return datetime.date(year, int(month), int(day))


# vrátí textový obsah pod elementem dle selektoru a ořízne bílé znaky
def get_first_content(element: Tag, selector: str) -> Optional[str]:
    results = element.select(selector)
    for result in results:
        return result.text.strip()
    return


def get_summary(event: VrbneEvent) -> str:
    if event.note:
        return "USD Vrbné: " + event.note
    else:
        return 'USD Vrbné'


# Se seznamu události vyrobí iCalendar (.ics) obsah
def ical(events: List[VrbneEvent]) -> str:
    cal = Calendar()
    cal.add('prodid', '-//vrbne-py')
    cal.add('version', '2.0')
    cal.add('name', "kanál České Vrbné")
    cal.add('description', "provoz slalomového kanálu")
    for event in events:
        cal_event = Event()
        cal_event.add("uid", uuid.uuid1())
        cal_event.add("dtstamp", datetime.datetime.now())
        cal_event.add("dtstart", event.datetime_from())
        cal_event.add("dtend", event.datetime_to())
        cal_event.add("summary", get_summary(event))
        cal_event.add("description", URL)
        cal.add_component(cal_event)

    return cal.to_ical().decode("UTF-8")


# Jen pro testy bez AWS
def main():
    events = get_events()
    #    for event in events:
    #        print(event)
    print(ical(events))


if __name__ == '__main__':
    main()
