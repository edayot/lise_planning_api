from bs4 import BeautifulSoup
import json
import requests
import os
from tqdm import tqdm
import logging

APP_URL = "https://lise.ensam.eu/"
WANTED_PLANNING = "https://lise.ensam.eu/faces/Planning.xhtml"
HOME_URL = "https://lise.ensam.eu/faces/MainMenuPage.xhtml"

PLANNING_FORM = "form:j_idt118"
PLANNING_FORM_SECOND = "form:j_idt244"
HOME_PLANNING_BUTTON = "form:j_idt806"


HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "content-type": "application/x-www-form-urlencoded",
    "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Linux\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1"
}


class CreatePlanning():
    def __init__(self) -> None:
        self.idinit = None
        self.viewstate = None
        self.session = requests.Session()
    
    def authenticate(self, username : str, password : str):
        cas_login_response = self.session.get(APP_URL)
        cas_login_response.raise_for_status()

        soup = BeautifulSoup(cas_login_response.text, "html.parser")
        execution_uuid = soup.find("input", {"name": "execution"}).get("value")


        data = {
            "username": username,
            "password": password,
            "execution": execution_uuid,
            "_eventId": "submit",
            "geolocation" : ""
        }

        lise_response = self.session.post(
            cas_login_response.url,
            data=data,
            headers=HEADERS,
            allow_redirects=True
        )
        self.modify_globals(lise_response)
    
    def modify_globals(self, lise_response : requests.Response):
        soup = BeautifulSoup(lise_response.text, "html.parser")
        self.idinit = soup.find("input", {"name": "form:idInit"}).get("value")
        self.viewstate = soup.find("input", {"name": "javax.faces.ViewState"}).get("value")
    
    def go_to_planning(self):
        data = {
            'form': 'form',
            'form:largeurDivCenter': '581',
            'form:idInit': self.idinit,
            'form:sauvegarde': '',
            'form:j_idt840_input': '44323',
            'javax.faces.ViewState': self.viewstate,
            HOME_PLANNING_BUTTON: HOME_PLANNING_BUTTON
        }

        planning_response = self.session.post(
            HOME_URL,
            data=data,
            headers=HEADERS,
            allow_redirects=True
        )
        self.modify_globals(planning_response)
    
    def get_planning(self):
        data = {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': PLANNING_FORM,
            'javax.faces.partial.execute': PLANNING_FORM,
            'javax.faces.partial.render': PLANNING_FORM,
            PLANNING_FORM: PLANNING_FORM,
            f'{PLANNING_FORM}_start': '0',
            f'{PLANNING_FORM}_end': '10710025200000',
            'form:idInit': self.idinit,
            f'{PLANNING_FORM_SECOND}_focus': '',
            f'{PLANNING_FORM_SECOND}_input': '44323',
            'javax.faces.ViewState': self.viewstate,
        }
        r = self.session.post(
            WANTED_PLANNING,
            data=data,
            headers=HEADERS,
            allow_redirects=True
        )
        soup = BeautifulSoup(r.text, "html.parser")

        for element in soup.find_all("update"):
            if element["id"] == PLANNING_FORM:
                planning = json.loads(element.string)
                return planning
        return None
    
    def get_event(self, event_id : str):
        data ={
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': PLANNING_FORM,
            'javax.faces.partial.execute': PLANNING_FORM,
            'javax.faces.partial.render': 'form:modaleDetail form:confirmerSuppression',
            'javax.faces.behavior.event': 'eventSelect',
            'javax.faces.partial.event': 'eventSelect',
            f'{PLANNING_FORM}_selectedEventId': f'{event_id}',
            'form:idInit': self.idinit,
            f'{PLANNING_FORM}_view': 'agendaWeek',
            f'{PLANNING_FORM_SECOND}_focus': '',
            f'{PLANNING_FORM_SECOND}_input': '44323',
            'javax.faces.ViewState': self.viewstate,
        }
        r = self.session.post(
            WANTED_PLANNING,
            data=data,
            headers=HEADERS,
            allow_redirects=True
        )
        soup = BeautifulSoup(r.text, "xml.parser")
        for element in soup.find_all("update"):
            if element["id"] == "form:modaleDetail":
                return element.string
        
    def get_all(self, username : str, password : str):
        self.authenticate(username, password)
        self.go_to_planning()
        planning = self.get_planning()
        events = {}
        for event in planning["events"]:
            event_id = event["id"]
            event = self.get_event(event_id)
            events[event_id] = event
        return planning, events



