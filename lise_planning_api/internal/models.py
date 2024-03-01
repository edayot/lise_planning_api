from dataclasses import dataclass
from ics import Event, Attendee
from datetime import datetime
from bs4 import BeautifulSoup


GLOBAL_INFO_FORM = "form:j_idt154_content"
RESSOURCES_FORM = "form:onglets:j_idt166_data"
INTERVENANTS_FORM = "form:onglets:j_idt174_data"
APPRENANTS_FORM = "form:onglets:apprenantsTable_data"
GROUPES_FORM = "form:onglets:j_idt213_data"
COURS_FORM = "form:onglets:j_idt221_data"

@dataclass
class Person:
    nom : str
    prenom : str

    def to_attendee(self):
        return Attendee(
            email=f"{self.nom} {self.prenom}"
        )

@dataclass
class Group:
    name_code: str
    name: str
    
    def __str__(self):
        return f"{self.name}"

@dataclass
class Ressource:
    code : str
    name : str

    def __str__(self):
        return f"{self.name} ({self.code})"

@dataclass
class Cours:
    code : str
    name : str
    module : str

    def __str__(self):
        return f"{self.name}, {self.module}"

@dataclass
class LiseEvent:
    id: str
    # html data
    status: str
    matiere: str
    type: str
    description: str
    is_exam: bool

    ressource: list[Ressource]
    intervenant: list[Person]
    apprenant: list[Person]
    groupe: list[Group]
    cours : list[Cours]


    # json data
    title: str
    is_all_day: bool
    start: str
    end: str

    formatting_desc: bool = True
    

    def from_data(html : str, data_dict : dict, formatting_desc=True) -> "LiseEvent":
        parsed_html = LiseEvent._parse_html(html)
        return LiseEvent(
            id = data_dict["id"],
            status = parsed_html["status"],
            matiere = parsed_html["matiere"],
            type = parsed_html["type"],
            description = parsed_html["description"],
            is_exam = parsed_html["is_exam"],
            ressource = parsed_html["ressource"],
            intervenant = parsed_html["intervenant"],
            apprenant = parsed_html["apprenant"],
            groupe = parsed_html["groupe"],
            cours = parsed_html["cours"],
            title = data_dict["title"],
            is_all_day = data_dict["allDay"],
            start = data_dict["start"],
            end = data_dict["end"],
            formatting_desc=formatting_desc,
        )



    def _parse_html(html : str) -> dict:
        soup = BeautifulSoup(html, 'html.parser')
        infos = LiseEvent._get_event_global_info(soup)
        ressources = LiseEvent._get_event_ressources(soup)
        intervenants = LiseEvent._get_event_intervenants(soup)
        apprenants = LiseEvent._get_event_apprenants(soup)
        groupes = LiseEvent._get_event_groupes(soup)
        cours = LiseEvent._get_event_cours(soup)
        return {
            "status": infos["status"],
            "matiere": infos["matiere"],
            "type": infos["type"],
            "description": infos["description"],
            "is_exam": infos["is_exam"],
            "ressource": ressources,
            "intervenant": intervenants,
            "apprenant": apprenants,
            "groupe": groupes,
            "cours": cours
        }


    def _get_event_global_info(soup : BeautifulSoup) -> dict:
        # find soup with id=GLOBAL_INFO_FORM
        souf_info = soup.find("div", {"id": GLOBAL_INFO_FORM})
        # find all infos
        for soup_info in souf_info.find_all("div", {"class": "ui-grid-row"}):
            # find the label
            divs = soup_info.find_all("div", {"class": "ui-panelgrid-cell ui-grid-col-6"})
            label = divs[0].text
            value = divs[1].text
            if label == "Statut":
                status = value
            elif label == "Matière":
                matiere = value
            elif label == "Type d'enseignement":
                type = value
            elif label == "Description":
                description = value
            elif label == "Est une épreuve":
                is_exam = value == "Oui"
            else:
                raise ValueError(f"Unknown label {label}")
        return {
            "status": status,
            "matiere": matiere,
            "type": type,
            "description": description,
            "is_exam": is_exam
        }

    def _get_event_ressources(soup : BeautifulSoup) -> list[Ressource]:
        soup_ressources = soup.find("tbody", {"id": RESSOURCES_FORM})
        ressources = []
        for soup_ressource in soup_ressources.find_all("tr"):
            tds = soup_ressource.find_all("td")
            code = tds[0].text.replace("\n", "").strip()
            if code == "Aucun enregistrement":
                return []
            name = tds[1].text.replace("\n", "").strip()
            ressources.append(Ressource(code, name))
        return ressources
    
    def _get_event_person(soup : BeautifulSoup, tbody_id : str) -> list[Person]:
        soup_person = soup.find("tbody", {"id": tbody_id})
        persons = []
        for soup_intervenant in soup_person.find_all("tr"):
            tds = soup_intervenant.find_all("td")
            nom = tds[0].text.replace("\n", "").strip()
            if nom == "Aucun enregistrement":
                return []
            prenom = tds[1].text.replace("\n", "").strip()
            persons.append(Person(nom, prenom))
        return persons

    def _get_event_intervenants(soup : BeautifulSoup) -> list[Person]:
        return LiseEvent._get_event_person(soup, INTERVENANTS_FORM)
    
    def _get_event_apprenants(soup : BeautifulSoup) -> list[Person]:
        return LiseEvent._get_event_person(soup, APPRENANTS_FORM)
    
    def _get_event_groupes(soup : BeautifulSoup) -> list[Group]:
        soup_groupes = soup.find("tbody", {"id": GROUPES_FORM})
        groupes = []
        for soup_groupe in soup_groupes.find_all("tr"):
            tds = soup_groupe.find_all("td")
            name_code = tds[0].text.replace("\n", "").strip()
            name = tds[1].text.replace("\n", "").strip()
            groupes.append(Group(name_code, name))
        return groupes

    def _get_event_cours(soup : BeautifulSoup) -> list[Cours]:
        soup_cours = soup.find("tbody", {"id": COURS_FORM})
        cours = []
        for soup_cour in soup_cours.find_all("tr"):
            tds = soup_cour.find_all("td")
            code = tds[0].text.replace("\n", "").strip()
            if code == "Aucun enregistrement":
                return []
            name = tds[1].text.replace("\n", "").strip()
            module = tds[2].text.replace("\n", "").strip()
            cours.append(Cours(code, name, module))
        return cours
    
    
    def to_ics(self) -> Event:
        e = Event()
        e.name = ", ".join([f"{r}" for r in self.cours])
        # self.start = "2024-05-28T14:40:00+0200"
        e.begin = datetime.strptime(self.start, "%Y-%m-%dT%H:%M:%S%z")
        e.end = datetime.strptime(self.end, "%Y-%m-%dT%H:%M:%S%z")
        e.description = self.get_description()
        e.location = ", ".join([f"{r}" for r in self.ressource])
        e.uid = self.id

        return e
    
    def get_description(self):

        
        bold = lambda x: f"<b>{x}</b>" if self.formatting_desc else lambda x: x

        cours_string = "\n".join([f"{c}" for c in self.cours])

        groupes_string = "\n".join([f"{g}" for g in self.groupe])

        apprenants_string = "\n".join([f"{a.nom} {a.prenom}" for a in self.apprenant])

        return f"""{bold("Intervenants : ")}{", ".join([f"{i.nom} {i.prenom}" for i in self.intervenant])}
{bold("Type : ")}{self.type} {"(Examen)" if self.is_exam else ""}
{bold("Statut : ")}{self.status}
{bold("Description : ")}{self.description}
{bold("Apprenants : ")}{len(self.apprenant)}

{bold("Cours :")}
{cours_string}

{bold("Groupes :")}
{groupes_string}

{bold("Apprenants :")}
{apprenants_string}
"""