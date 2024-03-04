from typing import Union

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from ics import Calendar
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Dict, Any
import hashlib

from lise_planning_api.internal.models import LiseEvent
from lise_planning_api.internal.scraping import CreatePlanning
from argon2 import PasswordHasher

import os

app = FastAPI()


@app.get(
    "/",
    responses={
        200: {
            "description": "Success message.",
            
        }
    }
)
def ping() -> str:
    """
    A ping endpoint to check if the API is up.
    """
    return "A simple API to create an ICS file from a Lise event."


class CachedResponse(BaseModel):
    content: Any
    timestamp: datetime
    password_hash: str

cache: Dict[str, CachedResponse] = {}

def verify_password(password: str, password_hash: str, ph : PasswordHasher) -> bool:
    try:
        return ph.verify(password_hash, password)
    except:
        return False


@app.get(
    "/{username}",
    responses={
        200: {
            "content": {
                "text/calendar": {
                    "example": """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
SUMMARY:Access-A-Ride Pickup
DTSTART;TZID=America/New_York:20130802T103400
DTEND;TZID=America/New_York:20130802T110400
LOCATION:1000 Broadway Ave.\, Brooklyn
DESCRIPTION: Access-A-Ride to 900 Jay St.\, Brooklyn
STATUS:CONFIRMED
SEQUENCE:3
BEGIN:VALARM
TRIGGER:-PT10M
DESCRIPTION:Pickup Reminder
ACTION:DISPLAY
END:VALARM
END:VEVENT
BEGIN:VEVENT
SUMMARY:Access-A-Ride Pickup
DTSTART;TZID=America/New_York:20130802T200000
DTEND;TZID=America/New_York:20130802T203000
LOCATION:900 Jay St.\, Brooklyn
DESCRIPTION: Access-A-Ride to 1000 Broadway Ave.\, Brooklyn
STATUS:CONFIRMED
SEQUENCE:3
BEGIN:VALARM
TRIGGER:-PT10M
DESCRIPTION:Pickup Reminder
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR
"""
                }
            },
            "description": "ICS file for the user's planning."
        }
    }
)
def get_ics(username: str, password: str, formatting_desc: str = "True"):
    """
    Get the ICS file for the user's planning.
    """
    ph = PasswordHasher()
    if username in cache:
        cached_response = cache[username]
        if datetime.now() - cached_response.timestamp < timedelta(minutes=10):
            if verify_password(password, cached_response.password_hash, ph):
                return StreamingResponse(cached_response.content, media_type="text/calendar", headers={"Content-Disposition": "attachment; filename=planning.ics"})
            else:
                del cache[username]
        else:
            del cache[username]

    # Get the planning
    planning, events = CreatePlanning().get_all(username, password)
    c = Calendar()
    for event_id, event_html in events.items():
        event: LiseEvent = LiseEvent.from_data(event_html, [event for event in planning["events"] if event["id"] == event_id][0], formatting_desc=formatting_desc == "True")
        c.events.add(event.to_ics())    

    serialized_content = c.serialize()
    cache[username] = CachedResponse(content=serialized_content, timestamp=datetime.now(), password_hash=ph.hash(password))

    return StreamingResponse(serialized_content, media_type="text/calendar", headers={"Content-Disposition": "attachment; filename=planning.ics"})