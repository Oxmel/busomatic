# Bus'O'Matic

![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)
[![Codacy Badge](https://img.shields.io/badge/code%20quality-B-brightgreen.svg)](https://www.codacy.com/app/Oxmel/busomatic?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Oxmel/busomatic&amp;utm_campaign=Badge_Grade)

## Description

Bus'O'Matic est une web app minimaliste permettant de trouver les horaires de passage des prochains bus / tram à un arrêt donné.
Avec dans l'optique de permettre une consultation sur un maximum de supports différents (smartphone, tablette, pc,...).

L'utilisateur choisit un numéro de ligne, une direction, et le nom de l'arrêt pour lequel il veut connaître les horaires.
Il obtient ensuite l'heure de passage (en temps réel) des 10 prochains bus / tram à cet arrêt.

Ce service s'appuie sur les [données](https://opendata.clermontmetropole.eu/explore/dataset/gtfs-smtc/information/) au format GTFS
et les [mises à jour](https://opendata.clermontmetropole.eu/explore/dataset/gtfs-smtc/table/) du trafic fournies
par la plateforme [opendata](https://opendata.clermontmetropole.eu/pages/accueil/) de Clermont-Ferrand.
La base de données SQLite est générée avec l'outil [gtfsdb](https://github.com/OpenTransitTools/gtfsdb).

## Screenshots

![initial-search](/screenshots/initial-search.png?raw=true)
![search-result](/screenshots/search-result.png?raw=true)

## Dépendances

    * bottle
    * requests
    * gtfs-realtime-bindings
