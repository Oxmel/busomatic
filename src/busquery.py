#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from urllib2 import Request, urlopen
import datetime
import json


# Check if navitia token has been set up
try :
    # Open the file containing the token in read only mode
    token_location = open('src/navitia-token', 'r')
    token = token_location.read().strip('\n')
except IOError :
    print "Error: This app requires an api key to access navitia api"
    print "Please check 'README.md' for more informations"


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
        # Ignore special lines (PDD, BEN, etc...)
        if len(line['code']) <= 2:
            line_name = line['code']
            line_id = line['id']
            lines_list.append((line_id,line_name))
    return lines_list

def get_routes(line_id):
    url = "https://api.navitia.io/v1/coverage/fr-se/lines/%s" %line_id
    data = query_data(url)
    routes_list = []
    for route in data['lines'][0]['routes']:
        route_name = route['direction']['stop_area']['name']
        route_id = route['id']
        routes_list.append((route_id,route_name))
    return routes_list


def get_stops(route_id):
    url = 'http://api.navitia.io/v1/coverage/fr-se/routes/%s?depth=3' %route_id
    stops = query_data(url)
    stops_list = []
    for stop in stops['routes'][0]['stop_points']:
        stop_name = stop['name']
        stop_id = stop['id']
        stops_list.append((stop_id,stop_name))
    return stops_list


def get_schedule(stop_id):
    url = "https://api.navitia.io/v1/coverage/fr-se/stop_points/%s/departures?count=10" %stop_id
    schedules = query_data(url)
    schedules_list = []
    for schedule in schedules['departures']:
        line_name = schedule['display_informations']['code']
        line_route = schedule['display_informations']['trip_short_name']
        line_time = schedule['stop_date_time']['arrival_date_time']
        # Arrival time comes as an ISO 8601 “YYYYMMDDThhmmss” string
        # So we convert it in a human readable format, e.g. HH:MM:SS (24h)
        convert_time = datetime.datetime.strptime(line_time, '%Y%m%dT%H%M%S')
        # Remove seconds
        line_htime = convert_time.time().strftime('%H:%M')
        schedules_list.append((line_name, line_route, line_htime))
    return schedules_list

