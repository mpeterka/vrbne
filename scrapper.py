import datetime
import re
import httpx
from bs4 import BeautifulSoup
from typing import List, Tuple, Optional
from models import VrbneEvent

URL = "http://itdev.cz/SlalomCourse/OpeningTimes.aspx"

async def fetch_events() -> List[VrbneEvent]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(URL)
            response.raise_for_status()
            html = response.text
        except httpx.HTTPError as e:
            print(f"HTTP error fetching events: {e}")
            return []
    
    soup = BeautifulSoup(html, features='html.parser')
    table = soup.find("table", class_="rgMasterTable")
    if not table:
        return []
        
    table_bodies = table.select("tbody")
    if not table_bodies:
        return []
        
    tbody = table_bodies[-1]
    rows = tbody.select("tr")
    
    events = []
    for row in rows:
        events.extend(parse_row(row))
    return events

def parse_row(row) -> List[VrbneEvent]:
    events = []
    try:
        date_str = get_first_content(row, "label")
        if not date_str:
            return []
            
        note_td = row.select("td[align=left]")
        note = note_td[0].text.strip() if note_td else ""
        
        hours = get_hours(row.select("td[align=center]"))
        
        event_date = parse_date(date_str)
        
        for time_from, time_to in hours:
            event = VrbneEvent(
                date=event_date,
                time_from=time_from,
                time_to=time_to,
                note=note
            )
            events.append(event)
    except Exception as e:
        # Log error in production
        print(f"Error parsing row: {e}")
        pass
    return events

def get_hours(cells) -> List[Tuple[str, str]]:
    hours_text = [cell.text.strip() for cell in cells if cell.text.strip()]
    if len(hours_text) == 2:
        return [(hours_text[0], hours_text[1])]
    elif len(hours_text) == 4:
        return [(hours_text[0], hours_text[1]), (hours_text[2], hours_text[3])]
    return []

def parse_date(day_month: str) -> datetime.date:
    year = datetime.date.today().year
    m = re.search(r'([0-9]{1,2})\.([0-9]{1,2})\.', day_month)
    if not m:
        raise ValueError(f"Invalid date format: {day_month}")
    day = int(m.group(1))
    month = int(m.group(2))
    return datetime.date(year, month, day)

def get_first_content(element, selector: str) -> Optional[str]:
    results = element.select(selector)
    if results:
        return results[0].text.strip()
    return None
