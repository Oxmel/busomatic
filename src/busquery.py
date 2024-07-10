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


class BusQuery():

    def __init__(self):

        self.feed = None
        self.refresh_feed = False
        self.journey = {
            'route_id': None,
            'direction_id': None,
            'stop_id': None,
            'cur_date': None,
            'weekday': None,
            'cur_time': None
        }


    def update_time(self):

        journey = self.journey
        journey['cur_date'] = date.today().strftime('%Y-%m-%d')
        journey['weekday'] = datetime.today().weekday()
        journey['cur_time'] = datetime.now().time().strftime('%H:%M:%S')


    def get_realtime_feed(self):

        url = gtfs_rt_url
        feed = gtfs_realtime_pb2.FeedMessage()
        response = requests.get(url)
        feed.ParseFromString(response.content)

        return feed


    def update_journey(self):

        self.feed = self.get_realtime_feed()
        self.update_time()


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


    def get_directions(self):

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

        directions = self.query_db(query, self.journey)
        return directions


    def get_stops(self):

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

        stops = self.query_db(query, self.journey)
        return stops


    def get_departures(self):

        departures = []

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
              R.route_short_name,
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

        next_departures = self.query_db(query, self.journey)

        for trip_id, route_name, dir_name, departure_time in next_departures:
            departure = {
                'trip_id': trip_id,
                'route_name': route_name,
                'direction_name':  dir_name,
                'scheduled_time': departure_time
            }

            departures.append(departure)

        return departures


    def get_realtime_schedule(self):

        # Use a snapshot of the gtfs-rt feed on initial search to display
        # results faster. Each auto refresh then also triggers a feed update
        if self.refresh_feed:
            self.update_journey()
        else:
            self.refresh_feed = True

        feed = self.feed
        realtime_schedule = []
        journey = self.journey
        stop_id = journey['stop_id']
        departures = self.get_departures()

        for departure in departures:
            trip_id = departure['trip_id']
            scheduled_time = departure['scheduled_time']
            departure_time = datetime.strptime(scheduled_time, '%H:%M:%S').time()

            for entity in feed.entity:
                if entity.HasField('trip_update') and entity.id == trip_id:
                    stop_time_update = entity.trip_update.stop_time_update

                    for update in stop_time_update:
                        if (update.stop_id == stop_id and update.HasField('departure') and
                            update.departure.HasField('delay') and update.departure.delay != 0):
                            delay = update.departure.delay
                            # Delay can be a positive or negative int, timedelta handles both
                            real_time = (datetime.combine(date.today(), departure_time) + timedelta(seconds=delay)).time()
                            departure_time = real_time

            realtime_schedule.append((departure['route_name'], departure['direction_name'], departure_time))

        return realtime_schedule
