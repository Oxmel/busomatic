#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Name : busquery.py

import os
import sqlite3
from google.transit import gtfs_realtime_pb2
import requests
from datetime import date, time,  datetime, timedelta

# Live feed for realtime updates
gtfs_rt_url = 'https://opendata.clermontmetropole.eu/api/explore/v2.1/catalog/datasets/gtfsrt_tripupdates/files/2c6b5c63d7be78905779d28500e6ab7e'

# The sqlite database is not located in this folder or any subfolder
# So we need to manually construct the full path to the db
# https://stackoverflow.com/a/14150750
path_to_db = os.path.abspath(__file__ + '/../../db/t2c-gtfs.db')
conn = sqlite3.connect(path_to_db)


# TODO: Update datetime infos for each refresh so next departures are also
# updated accordingly
class BusQuery():

    def __init__(self):

        self.journey = {
            'route_id': None,
            'direction_id': None,
            'stop_id': None,
            'cur_date': date.today().strftime('%Y-%m-%d'),
            'weekday': datetime.today().weekday(),
            'cur_time': datetime.now().time().strftime('%H:%M:%S')
        }


    def get_realtime_feed(self, url):

        feed = gtfs_realtime_pb2.FeedMessage()
        response = requests.get(url)
        feed.ParseFromString(response.content)

        return feed


    # Using 'param=None' to check if param exists because 'journey' is a dict
    # So if we try to use *args or **kwargs, it will be unpacked instead of
    # being passed as is in the query. Which will raise an error.
    def query_db(self, query, journey=None):

        cur = conn.cursor()
        if journey:
            cur.execute(query, journey)
        else:
            cur.execute(query)
        response = cur.fetchall()
        cur.close()

        return response


    # Original GTFS contains a lot of special lines we don't need
    # So we filter lines by name and size to get regular services only
    def get_lines(self):

        query = """
            SELECT route_id,
              route_long_name
            FROM routes
            WHERE route_long_name LIKE 'T%'
              OR route_long_name LIKE 'L%'
              AND length(route_long_name) < 9
            ORDER BY route_short_name + 0 ASC
        """

        lines = self.query_db(query)
        return lines


    def get_directions(self, line_id):

        journey = self.journey
        journey['route_id'] = line_id

        query = """
            WITH valid_services AS (
              SELECT service_id
              FROM calendar
              WHERE start_date <= :cur_date
                AND end_date >= :cur_date
                AND (CASE :weekday
                      WHEN 0 THEN monday
                      WHEN 1 THEN tuesday
                      WHEN 2 THEN wednesday
                      WHEN 3 THEN thursday
                      WHEN 4 THEN friday
                      WHEN 5 THEN saturday
                      WHEN 6 THEN sunday
                      END) = 1
              UNION
              SELECT service_id
              FROM calendar_dates
              WHERE date = :cur_date
                AND exception_type = 1
              EXCEPT
              SELECT service_id
              FROM calendar_dates
              WHERE date = :cur_date
                AND exception_type = 2
            )
            SELECT DISTINCT
              T.direction_id,
              T.trip_headsign
            FROM stop_times ST
            JOIN trips T ON T.trip_id = ST.trip_id
            JOIN routes R ON R.route_id = T.route_id
            JOIN valid_services VS ON VS.service_id = T.service_id
            WHERE R.route_id = :route_id
              AND ST.departure_time >= :cur_time
        """

        directions = self.query_db(query, journey)
        return directions


    def get_stops(self, direction_id):

        journey = self.journey
        journey['direction_id'] = direction_id

        query = """
            WITH valid_services AS (
              SELECT service_id
              FROM calendar
              WHERE start_date <= :cur_date
                AND end_date >= :cur_date
                AND (CASE :weekday
                      WHEN 0 THEN monday
                      WHEN 1 THEN tuesday
                      WHEN 2 THEN wednesday
                      WHEN 3 THEN thursday
                      WHEN 4 THEN friday
                      WHEN 5 THEN saturday
                      WHEN 6 THEN sunday
                    END) = 1
              UNION
              SELECT service_id
              FROM calendar_dates
              WHERE date = :cur_date
                AND exception_type = 1
              EXCEPT
              SELECT service_id
              FROM calendar_dates
              WHERE date = :cur_date
                AND exception_type = 2
            ),
            route_trips AS (
              SELECT trip_id
              FROM trips
              WHERE route_id = :route_id
                AND direction_id = :direction_id
                AND service_id IN (SELECT service_id FROM valid_services)
            )
            SELECT DISTINCT
              S.stop_id,
              S.stop_name
            FROM stop_times ST
            JOIN stops S ON S.stop_id = ST.stop_id
            JOIN route_trips RT ON RT.trip_id = ST.trip_id
            ORDER BY ST.stop_sequence

        """

        stops = self.query_db(query, journey)
        return stops


    def get_departures(self, stop_id):

        journey = self.journey
        departures = []
        journey['stop_id'] = stop_id

        query = """
            WITH valid_services AS (
              SELECT service_id
              FROM calendar
              WHERE start_date <= :cur_date
                AND end_date >= :cur_date
                AND (CASE :weekday
                      WHEN 0 THEN monday
                      WHEN 1 THEN tuesday
                      WHEN 2 THEN wednesday
                      WHEN 3 THEN thursday
                      WHEN 4 THEN friday
                      WHEN 5 THEN saturday
                      WHEN 6 THEN sunday
                    END) = 1
              UNION
              SELECT service_id
              FROM calendar_dates
              WHERE date = :cur_date
                AND exception_type = 1
              EXCEPT
              SELECT service_id
              FROM calendar_dates
              WHERE date = :cur_date
                AND exception_type = 2
            )
            SELECT DISTINCT
              ST.trip_id,
              R.route_long_name,
              T.trip_headsign,
              ST.departure_time
            FROM stop_times ST
            JOIN trips T ON T.trip_id = ST.trip_id
            JOIN routes R ON R.route_id = T.route_id
            JOIN valid_services VS ON VS.service_id = T.service_id
            WHERE ST.stop_id = :stop_id
              AND ST.departure_time >= :cur_time
            ORDER BY ST.departure_time
            LIMIT 10

        """

        next_departures = self.query_db(query, journey)

        for entry in next_departures:
            departure = {
                'trip_id': entry[0],
                'route_name': entry[1],
                'direction_name':  entry[2],
                'scheduled_time': entry[3]
            }

            departures.append(departure)

        return departures


    def get_realtime_schedule(self, stop_id):

        journey = self.journey
        departures = self.get_departures(stop_id)
        realtime_schedule = []
        feed = self.get_realtime_feed(gtfs_rt_url)

        for departure in departures:
            stop_id = journey['stop_id']
            trip_id = departure['trip_id']

            for entity in feed.entity:
                if entity.id == trip_id:
                    updates = entity.trip_update.stop_time_update

                    for update in updates:
                        if update.stop_id == stop_id:
                            if update.departure.delay != 0:
                                delay = update.departure.delay
                                scheduled_time = departure['scheduled_time']
                                time_object = datetime.strptime(scheduled_time, '%H:%M:%S').time()
                                # Delay can be a positive or negative int, timedelta handles both
                                real_time = (datetime.combine(date.today(), time_object) + timedelta(seconds=delay)).time()
                                departure['scheduled_time'] = real_time

            realtime_schedule.append((departure['route_name'], departure['direction_name'], departure['scheduled_time']))

        return realtime_schedule
