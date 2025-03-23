"""
Module pour récupérer les events de ICAL sur l'ISNA Rouen
"""

import datetime
import requests
import icalendar
import pytz


def fetch_ical_events(ical_url):
    """Retrieve and parse events from the iCal URL."""
    response = requests.get(ical_url)
    calendar = icalendar.Calendar.from_ical(response.content)
    return calendar


def get_week_events(calendar, timezone):
    """Retrieve events for the current week from the parsed iCal calendar."""
    events = []
    now = datetime.datetime.now(tz=timezone)
    start_of_week = now - datetime.timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_of_week = start_of_week + datetime.timedelta(days=7)

    for component in calendar.walk():
        if component.name == "VEVENT":
            event_start = component.get("dtstart").dt
            if isinstance(event_start, datetime.datetime):
                event_start = event_start.astimezone(timezone)
            if start_of_week <= event_start < end_of_week:
                events.append(component)
    return events


def get_day_events(calendar, timezone):
    """Retrieve events for the current day from the parsed iCal calendar."""
    events = []
    now = datetime.datetime.now(tz=timezone)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    for component in calendar.walk():
        if component.name == "VEVENT":
            event_start = component.get("dtstart").dt
            if isinstance(event_start, datetime.datetime):
                event_start = event_start.astimezone(timezone)
            if start_of_day <= event_start < end_of_day:
                events.append(component)
    return events


def format_event_time(event, timezone):
    """Format the event time to HH:MM - HH:MM summary."""
    start = event.get("dtstart").dt
    end = event.get("dtend").dt

    if isinstance(start, datetime.datetime) and isinstance(
        end, datetime.datetime
    ):
        start = start.astimezone(timezone)
        end = end.astimezone(timezone)
        start_time = start.strftime("%H:%M")
        end_time = end.strftime("%H:%M")
        return f"{start_time}-{end_time}"
    return "All day"


if __name__ == "__main__":
    # iCal URL for the INSA calendar
    ical_url = "https://ade.insa-rouen.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?calType=ical&projectId=8&resources=356&firstDate=2024-08-01&lastDate=2025-07-31"

    # Define timezone
    timezone = pytz.timezone("Europe/Paris")

    # Fetch and parse the calendar
    calendar = fetch_ical_events(ical_url)

    # Get and print week's events
    print("Week Events:")
    week_events = get_week_events(calendar, timezone)
    for event in sorted(week_events, key=lambda x: x.get("dtstart").dt):
        time_range = format_event_time(event, timezone)
        print(f"{time_range} {event.get('summary')}")

    # Get and print day's events
    print("\nDay Events:")
    day_events = get_day_events(calendar, timezone)
    for event in day_events:
        time_range = format_event_time(event, timezone)
        print(f"{time_range} {event.get('summary')}")
