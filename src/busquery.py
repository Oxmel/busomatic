#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Name : busquery.py

import os
import sqlite3
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup

# The sqlite database is not located in this folder or any subfolder
# So we need to manually construct the full path to the db
# https://stackoverflow.com/a/14150750
path_to_db = os.path.abspath(__file__ + '/../../db/busomatic-db.sq3')

# Perform db calls using either static sql queries or queries with variables
def database(query, *args):
    conn = sqlite3.connect(path_to_db)
    cur = conn.cursor()
    cur.execute(query, args)
    response = cur.fetchall()
    cur.close
    return response

# Gather schedule for selected stop
# The infos we're looking for (line name, direction, passage time) are
# all contained in a single table. So we focus each table rows and extract
# the values in the data containers (<td>)
def horaire(id_arret):
    url = ('http://qr.t2c.fr/qrcode?_stop_id=' + id_arret)
    conn = urllib.request.urlopen(url)
    soup = BeautifulSoup(conn, from_encoding='utf-8', features='html.parser')
    schedule=[]
    # We skip the first table row as it doesn't contain anything relevant
    for item in soup.find_all('tr')[1:]:
        # Same goes for the third data container
        line_info = item.find_all('td')[:3]
        # Line name
        line_name = line_info[0].get_text().strip()
        # Line direction
        line_dir = line_info[1].get_text().strip()
        # Passage time
        line_time = line_info[2].get_text().strip()
        # Create a tuple with the infos and add it in the list
        schedule.append((line_name,line_dir,line_time))
    conn.close()
    return schedule
