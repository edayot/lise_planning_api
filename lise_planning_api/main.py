from typing import Union

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from ics import Calendar

from lise_planning_api.internal.models import LiseEvent
from lise_planning_api.internal.scraping import CreatePlanning

import os

app = FastAPI()


@app.get("/")
def read_root():
    return "A simple API to create an ICS file from a Lise event."


@app.get("/get_ics")
def get_ics(
    username: str,
    password: str,
):
    # example : /get_ics?username=your_username&password=your_password
    
    planning, events = CreatePlanning().get_all(username, password)

    # Create the ics file
    c = Calendar()
    for event_id, event_html in events.items():
        event : LiseEvent = LiseEvent.from_data(event_html, [event for event in planning["events"] if event["id"] == event_id][0])
        c.events.add(event.to_ics())    

    return StreamingResponse(c.serialize(), media_type="text/calendar", headers={"Content-Disposition": "attachment; filename=planning.ics"})



