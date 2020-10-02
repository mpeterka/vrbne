import datetime
import logging
import re
import urllib.request
from typing import List, Tuple, Optional

from bs4 import BeautifulSoup, ResultSet, Tag
from handler_vrbne_event import VrbneEvent

logger = logging.getLogger()
logger.setLevel(logging.INFO)

URL = "http://itdev.cz/SlalomCourse/OpeningTimes.aspx"


# Parsuje HTML a sestavuje z něho z seznam událostí
def get_events() -> List[VrbneEvent]:
    logger.info("Loading {0}".format(URL))
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
            logger.debug("Event found: {0}".format(event.__str__()))
            events.append(event)
    except Exception:
        logger.exception("Nepodařilo se načíst řádek")
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
