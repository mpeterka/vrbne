import logging

import pytz
from handler_ical import ical
from handler_scrapper import get_events
from handler_weather import set_weather

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#
# Stahuje z http://itdev.cz/SlalomCourse/OpeningTimes.aspx a vyrábí z něho icalendar pro import do kalendáře
#

TZ = pytz.timezone("Europe/Prague")

# AWS Lambda entrypoint
def icalendar(event, context):
    events = get_events()
    set_weather(events)
    body = ical(events)

    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/calendar; charset=utf-8"
        },
        "body": body
    }

    logger.debug(body)

    return response


# Jen pro testy bez AWS
def main():
    logging.basicConfig(level=logging.DEBUG)
    events = get_events()
    set_weather(events)
    #    for event in events:
    #        print(event)
    print(ical(events))


if __name__ == '__main__':
    main()
