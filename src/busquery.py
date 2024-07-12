#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Name : busquery.py

import os
import sqlite3
import requests
import threading
from google.transit import gtfs_realtime_pb2
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

        self.journey = {}
        self.local_feed = None
        self.use_local_feed = False


    def update_journey(self, **kwargs):

        now = datetime.now()

        journey = self.journey
        cur_date = date.today().strftime('%Y-%m-%d')
        weekday = datetime.today().weekday()
        cur_time = now.time().strftime('%H:%M:%S')
        cur_time_obj = now

        self.journey.update(cur_date=cur_date, weekday=weekday, cur_time=cur_time, cur_time_obj=cur_time_obj)
        self.journey.update(kwargs)


    def get_realtime_feed(self):

        url = gtfs_rt_url
        feed = gtfs_realtime_pb2.FeedMessage()
        try:
            # Timeout triggers if the server doesn't answer for x secs
            # It's not a time limit on the entire response download
            response = requests.get(url, timeout=5)
            feed.ParseFromString(response.content)
            return feed
        # Catchall for any Requests exception
        except requests.exceptions.RequestException:
            return None


    def update_feed(self):
        self.local_feed = self.get_realtime_feed()
        self.use_local_feed = True

    # Endpoint response ranges from ~200ms to several seconds so we use
    # threading to download feed in parallel and avoid blocking page load
    def update_feed_thread(self):
        request_thread = threading.Thread(target=self.update_feed)
        request_thread.start()


    def convert_time(self, time_str):

        time_obj = datetime.strptime(time_str, '%H:%M:%S').time()
        convert_time = datetime.combine(date.today(), time_obj)

        return convert_time

    # Display remaining time in minutes for the first 3 results but only if
    # remaining minutes < 60. Otherwise display normal departure times
    def format_time(self, index, time_obj):

        now = datetime.now()

        # 'time_obj' is departure time + real time delay (positive or negative)
        # And if a line has too much advance 'now' can sometimes be greater
        # than 'time_obj' giving a wrong result with a -24h delta
        if now < time_obj:
            time_delta = time_obj - now
            round_delta = time_delta.seconds // 60
        else:
            round_delta = 0

        if index <= 2 and round_delta <= 0:
            format_time = ('<1min')
        elif index <= 2 and round_delta < 60:
            format_time = str(round_delta) + "'"
        else:
            format_time = time_obj.time().strftime('%H:%M')

        return format_time


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


    def get_directions(self, journey):

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


    def get_stops(self, journey):

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


    def get_departures(self, journey):

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

        next_departures = self.query_db(query, journey)

        for trip_id, route_name, dir_name, departure_time in next_departures:
            departure = {
                'trip_id': trip_id,
                'route_name': route_name,
                'direction_name':  dir_name,
                'scheduled_time': departure_time
            }

            departures.append(departure)

        return departures


    def get_realtime_schedule(self, feed, stop_id, departures):

        realtime_schedule = []

        for index, departure in enumerate(departures):
            trip_id = departure['trip_id']
            scheduled_time = departure['scheduled_time']
            time_obj = self.convert_time(scheduled_time)

            for entity in feed.entity:
                if entity.HasField('trip_update') and entity.id == trip_id:
                    stop_time_update = entity.trip_update.stop_time_update

                    for update in stop_time_update:
                        if (update.stop_id == stop_id and update.HasField('departure') and
                            update.departure.HasField('delay') and update.departure.delay != 0):
                            delay = update.departure.delay
                            # Delay can be a positive or negative int, timedelta handles both
                            time_obj = (time_obj + timedelta(seconds=delay))

            departure_time = self.format_time(index, time_obj)
            realtime_schedule.append((departure['route_name'], departure['direction_name'], departure_time))

        return realtime_schedule
