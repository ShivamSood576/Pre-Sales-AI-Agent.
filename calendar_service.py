import os
from datetime import datetime, timedelta
from uuid import uuid4

from google_auth import get_calendar_service

DEFAULT_TIME_ZONE = os.getenv("CALENDAR_TIME_ZONE", "Asia/Kolkata")
DEFAULT_CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")


def get_free_busy(start_time, end_time, calendar_id=DEFAULT_CALENDAR_ID):
    service = get_calendar_service()

    body = {
        "timeMin": start_time.isoformat(),
        "timeMax": end_time.isoformat(),
        "items": [{"id": calendar_id}],
    }

    result = service.freebusy().query(body=body).execute()
    return result["calendars"][calendar_id]["busy"]


def get_busy_slots(calendar_id=DEFAULT_CALENDAR_ID, hours_ahead=24):
    now = datetime.utcnow().replace(microsecond=0)
    end = now + timedelta(hours=hours_ahead)
    return get_free_busy(now, end, calendar_id=calendar_id)


def book_event(
    start_time,
    end_time,
    user_email,
    summary="Consultation",
    calendar_id=DEFAULT_CALENDAR_ID,
    organizer_email=None,
    time_zone=DEFAULT_TIME_ZONE,
):
    service = get_calendar_service()

    attendees = []
    if organizer_email:
        attendees.append({"email": organizer_email})
    attendees.append({"email": user_email})

    event = {
        "summary": summary,
        "description": "Consultation Call",
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": time_zone,
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": time_zone,
        },
        "attendees": attendees,
        "conferenceData": {
            "createRequest": {
                "requestId": uuid4().hex
            }
        },
    }

    created_event = service.events().insert(
        calendarId=calendar_id,
        body=event,
        conferenceDataVersion=1,
    ).execute()

    meet_link = None
    conference = created_event.get("conferenceData") or {}
    entry_points = conference.get("entryPoints") or []
    if entry_points:
        meet_link = entry_points[0].get("uri")

    return {
        "event_link": created_event.get("htmlLink"),
        "meet_link": meet_link,
    }
