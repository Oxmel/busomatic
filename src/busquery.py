#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from urllib2 import Request, urlopen
import json


# Check if navitia token has been set up
try :
    # Open the file containing the token in read only mode
    token_location = open('src/navitia-token', 'r')
    token = token_location.read().strip('\n')
except IOError :
    print "Warning: This app requires a token to access navitia api"
    print "Please check /src/navitia-token-readme for more informations"


# Generic function to perform api calls and make the json response readable
def query_data(url):
    req = Request(url)
    req.add_header('Authorization', token)
    response = urlopen(req).read()
    data = json.loads(response)
    return data


def get_lines():
    url = "https://api.navitia.io/v1/coverage/fr-se/networks/network:T2C/lines?count=500"
    data = query_data(url)
    lines_list = []
    for line in data['lines']:
        line_name = line['code']
        line_id = line['id']
        # Position of the current line in the list
        index = data['lines'].index(line)
        lines_list.append((line_id,line_name))
    return lines_list


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
    conn = urllib.urlopen(url)
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
