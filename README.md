# Lise planning API

Cet API permet à l'utilsateur d'exporter les données de Lise.


## Utilisation


### APi de Lise
Lise met à disposition cette route API : `https://lise.ensam.eu/ical_apprenant/2021-XXXX`

Elle permet d'exporter le calendrier sur lise de la semaine en cours et de la semaine d'après au format `.ics`. Elle peut ensuite être intégrée à Google Calendar.

### Ce projet

Ce projet enlève la limite des deux semaines en exportant la totalité du calendrier, elle utilise aussi des noms d'événements plus court et met tout dans la description.

Un inconvénient est qu'elle utilise un mot de passe pour se connecter. Il doit aussi être encodé pour être un URL.

Route API : `0.0.0.0:8000/2021-XXXX?password=PASSWORD`


## Installation

Il y a deux façons d'installer ce projet, soit en utilisant Docker, tout est automatisé, soit en installant poetry.


```bash
git clone https://github.com/edayot/lise_planning_api.git
cd lise_planning_api

# Avec docker
docker compose up

# Avec poetry
poetry install
poetry run app
```

Après ça l'API est accessible sur le port `8000`.

### Variables d'environnement

On peut créer un fichier `.env` pour configurer l'API

```bash
DEBUG=True # Active le reload automatique, False par défaut
PORT=8000 # Port de l'API, 8000 si non spécifié
```


### Anonymisation des passwords dans les logs

Pour ne pas afficher les mots de passe dans les logs, on utilise une version custom de uvicorn. Elle est installée automatiquement avec poetry.

Elle accessible à [ici](https://github.com/edayot/uvicorn) et modifie le fichier `uvicorn/protocols/utils.py` pour modifier la fonction `get_path_with_query_string`.

Code modifié :
```python

# Ancienne version
def get_path_with_query_string(scope: WWWScope) -> str:
    path_with_query_string = urllib.parse.quote(scope["path"])
    if scope["query_string"]:
        path_with_query_string = "{}?{}".format(
            path_with_query_string, scope["query_string"].decode("ascii")
        )
    return path_with_query_string


# Nouvelle version
def get_path_with_query_string(scope: WWWScope) -> str:
    path_with_query_string = urllib.parse.quote(scope["path"])
    if scope["query_string"]:
        query_string = scope["query_string"].decode("ascii")
        query_params = urllib.parse.parse_qs(query_string)
        for key, value in query_params.items():
            if key.lower() == 'password':
                query_params[key] = ['*' * 8]
        encoded_query_params = urllib.parse.urlencode(query_params, doseq=True)
        path_with_query_string = "{}?{}".format(path_with_query_string, encoded_query_params)
        path_with_query_string = path_with_query_string.replace('%2A', '*')
    return path_with_query_string
```



