# Bus'O'Matic
![Python Version](https://img.shields.io/badge/python-2.7-orange.svg)
[![Codacy Badge](https://img.shields.io/badge/code%20quality-B-brightgreen.svg)](https://www.codacy.com/app/Oxmel/busomatic?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Oxmel/busomatic&amp;utm_campaign=Badge_Grade)
![License Badge](https://img.shields.io/badge/license-GPLv3-blue.svg)


## Description

Bus'O'Matic est une web app minimaliste offrant la possibilité de trouver les
horaires de passage des prochains bus / tram à un arrêt donné. Avec dans
l'optique de permettre une consultation sur un maximum de supports différents
(smartphone, tablette, pc,...).

L'utilisateur choisit un numéro de ligne, une direction, et le nom de l'arrêt
pour lequel il veut connaître les horaires. Il obtient ensuite l'heure de
passage des 10 prochains bus / tram à cet arrêt.

Les données de transport sont publiées sous licence ODBL sur [transport.data.gouv.fr](https://transport.data.gouv.fr/datasets/aom/34) et directement exploitables via l'api de [navitia.io](https://navitia.opendatasoft.com/explore/dataset/fr-se/table/).


## Screenshots

![initial-search](/screenshots/initial-search.png?raw=true)
![search-result](/screenshots/search-result.png?raw=true)

## Utilisation

**1 - Installer les dépendances et cloner le repo:**

    git clone https://github.com/Oxmel/busomatic.git
    pip install bottle

**2 - Ajouter un token d'accès à l'api navitia (obligatoire):**

Créer un fichier `navitia-token` dans le dossier `/src` et y enregistrer le token d'accès. 

Pour récupérer un token il suffit de créer un compte sur [navitia.io](https://www.navitia.io/register/). Le free plan permet d'effectuer jusqu'à 20K requêtes / mois sur l'api.

**3 - Ajouter un token d'accès à l'api openweather (optionnel):**

Créer un fichier `openweather-token` dans le dossier `/src` et y enregistrer le token d'accès.

Cette étape n'est pas obligatoire mais est nécessaire si l'on souhaite afficher les infos météo. Et il est là aussi possible de récupérer un token gratuitement en créant un compte sur [openweathermap.org](https://home.openweathermap.org/users/sign_up). 