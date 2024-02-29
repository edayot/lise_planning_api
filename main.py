from typing import Union

from fastapi import FastAPI
from fastapi.responses import FileResponse
from ics import Calendar

from internal.models import LiseEvent
from internal.scraping import CreatePlanning

import os

app = FastAPI()


@app.get("/")
def read_root():
    return "A simple API to create an ICS file from a Lise event."


@app.get("/get_ics")
async def get_ics(
    username: str,
    password: str,
):
    
    planning, events = CreatePlanning().get_all(username, password)

    # Create the ics file
    c = Calendar()
    for event_id, event_html in events.items():
        event : LiseEvent = LiseEvent.from_data(event_html, [event for event in planning["events"] if event["id"] == event_id][0])
        c.events.add(event.to_ics())
    
    os.makedirs("__pycache__/planning", exist_ok=True)
    with open(f"__pycache__/planning/{username}.ics", "w") as my_file:
        my_file.writelines(c)

    return FileResponse(f"__pycache__/planning/{username}.ics", media_type="text/calendar", filename=f"{username}.ics")
    
    
