"""
Module pour récuperer les events de google calendar
"""

import datetime
import os.path
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz
from dotenv import load_dotenv

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_credentials():
    """Retrieve or refresh Google API credentials."""
    creds = None
    TOKEN_PATH = os.path.expanduser("~/.config/gcal_token.json")
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as e:
                print(f"Token refresh failed: {e}. Initiating new OAuth flow.")
                # Remove the invalid token file
                if os.path.exists(TOKEN_PATH):
                    os.remove(TOKEN_PATH)
                # Trigger a new OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    return creds


def get_events(service, calendar_ids, time_min, time_max):
    """Fetch events from the specified calendars within a given time range and associate them with their calendar names."""
    all_events = []
    for calendar_name, calendar_id in calendar_ids.items():
        try:
            events_result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])
            for event in events:
                event["calendar_name"] = calendar_name  # Associate the calendar name with the event
            all_events.extend(events)
        except HttpError as error:
            print(f"An error occurred with calendar {calendar_name}: {error}")
    return all_events


def get_today_events(service, calendar_ids):
    """Retrieve all events for the current day from specified calendars."""
    now = datetime.datetime.now()
    local_tz = datetime.datetime.now().astimezone().tzinfo
    now = datetime.datetime.now(local_tz)
    start_of_day = (
        now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    )
    end_of_day = (
        now.replace(
            hour=23, minute=59, second=59, microsecond=999999
        ).isoformat()
    )
    return get_events(service, calendar_ids, start_of_day, end_of_day)


def get_week_events(service, calendar_ids):
    """Retrieve all events for the current week from specified calendars."""
    now = datetime.datetime.utcnow()
    start_of_week = (now - datetime.timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_of_week = start_of_week + datetime.timedelta(
        days=6, hours=23, minutes=59, seconds=59, microseconds=999999
    )

    start_of_week_str = start_of_week.isoformat() + "Z"
    end_of_week_str = end_of_week.isoformat() + "Z"

    return get_events(service, calendar_ids, start_of_week_str, end_of_week_str)


def format_event_time(event):
    """Format the event time to HH:MM - HH:MM."""
    start = event["start"].get("dateTime")
    end = event["end"].get("dateTime")
    if start and end:
        start_time = datetime.datetime.fromisoformat(start).strftime("%H:%M")
        end_time = datetime.datetime.fromisoformat(end).strftime("%H:%M")
        return f"{start_time}-{end_time}"
    return "All day"

def complete_today_events():
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    # Load environment variables from .env file
    load_dotenv()

    calendar_ids = {
        "Perso": os.getenv("CALENDAR_ID_PERSO"),
        "Pro": os.getenv("CALENDAR_ID_PRO"),
        "Famille": os.getenv("CALENDAR_ID_FAMILLE"),
    }
    print("Today's events:")
    today_events = get_today_events(service, calendar_ids)
    return today_events

def main():
    """Shows usage of the Google Calendar API by printing today's and this week's events."""
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    # Load environment variables from .env file
    load_dotenv()

    calendar_ids = {
        "Perso": os.getenv("CALENDAR_ID_PERSO"),
        "Pro": os.getenv("CALENDAR_ID_PRO"),
        "Famille": os.getenv("CALENDAR_ID_FAMILLE"),
    }
    print("Today's events:")
    today_events = get_today_events(service, calendar_ids)
    for event in today_events:
        time_range = format_event_time(event)
        print(f"{time_range}  : ({event['calendar_name']}) {event['summary']}")

    print("\nThis week's events:")
    week_events = get_week_events(service, calendar_ids)
    week_events.sort(key=lambda event: event["start"].get("dateTime", event["start"].get("date")))
    for event in week_events:
        time_range = format_event_time(event)
        event_date = datetime.datetime.fromisoformat(event["start"].get("dateTime", event["start"].get("date")))
        day_of_week = event_date.strftime("%A")
        print(f"{day_of_week} {time_range} : ({event['calendar_name']}) {event['summary']}")



if __name__ == "__main__":
    main()
