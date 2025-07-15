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
gtfs_rt_url = 'https://opendata.clermontmetropole.eu/api/explore/v2.1/catalog/datasets/gtfs-smtc/files/2c6b5c63d7be78905779d28500e6ab7e'

# The sqlite database is not located in this folder or any subfolder
# So we need to manually construct the full path to the db
# https://stackoverflow.com/a/14150750
path_to_db = os.path.abspath(__file__ + '/../../db/t2c-gtfs.db')
conn = sqlite3.connect(path_to_db)


class BusQuery():

    def __init__(self):

        self.journey = {}
        self.local_feed = None
        self.refresh_feed = True


    def update_journey(self, **kwargs):

        now = datetime.now()

        journey = self.journey
        cur_date = date.today().strftime('%Y-%m-%d')
        weekday = datetime.today().weekday()
        cur_time = now.time().strftime('%H:%M:%S')
        cur_time_obj = now

        self.journey.update(cur_date=cur_date, weekday=weekday,
                            cur_time=cur_time, cur_time_obj=cur_time_obj, **kwargs)


    def get_realtime_feed(self):

        url = gtfs_rt_url
        feed = gtfs_realtime_pb2.FeedMessage()
        try:
            # Timeout triggers if the server doesn't answer for x secs
            # It's not a time limit on the entire response download
            response = requests.get(url, timeout=5)
            feed.ParseFromString(response.content)
            return feed
        # Fallback to prevent crashes if anything fails when parsing feed
        except:
            return None


    def update_feed(self):
        self.local_feed = self.get_realtime_feed()
        self.refresh_feed = False

    # Endpoint response ranges from ~200ms to several seconds so we use
    # threading to download feed in parallel and avoid blocking page load
    def update_feed_thread(self):
        request_thread = threading.Thread(target=self.update_feed)
        request_thread.start()


    # Use the version in cache when displaying results to ensure consistent
    # loading times. And get the latest version when results are refreshed
    def select_feed(self):

        if self.refresh_feed:
            feed = self.get_realtime_feed()
        else:
            feed = self.local_feed
            self.refresh_feed = True

        return feed


    # If next departure is after midnight (e.g. '00:15:00'), gtfs time format
    # will look like '24:15:00'. So we first get today's date, set time to
    # '00:00:00' and then use departure time as time delta.
    def convert_time(self, time_str):

        split_time = time_str.split(':')
        hours, minutes, seconds = int(split_time[0]), int(split_time[1]), int(split_time[2])
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        convert_time = now + timedelta(hours=hours, minutes=minutes, seconds=seconds)

        return convert_time


    # Display remaining time in minutes for the first 3 results but only if
    # remaining minutes < 60. Otherwise display normal departure times
    def format_time(self, time_obj):

        now = datetime.now()

        # 'time_obj' is departure time + real time delay (positive or negative)
        # And if a line has too much advance 'now' can sometimes be greater
        # than 'time_obj' giving a wrong result with a -24h delta
        if now < time_obj:
            time_delta = time_obj - now
            round_delta = time_delta.seconds // 60
        else:
            round_delta = 0

        # Convert any passage time that is less than 60 mins
        if round_delta < 60:
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
              route_desc
            FROM routes
            WHERE route_desc LIKE 'T%'
              OR route_desc LIKE 'L%'
              AND length(route_desc) < 9
            ORDER BY route_short_name + 0 ASC
        """

        lines = self.query_db(query)
        return lines

    # Extract the stop name that has the highest stop sequence for each
    # direction (aka terminus). Also use temporal data to follow shape
    # variations and potential terminus change between weekdays and weekends.
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
            SELECT trips.direction_id, stops.stop_name
            FROM stop_times
            INNER JOIN (
                SELECT t.trip_id, t.direction_id, MAX(st.stop_sequence) AS max_stop_sequence
                FROM trips t
                JOIN stop_times st ON t.trip_id = st.trip_id
                JOIN valid_services vs ON t.service_id = vs.service_id
                WHERE t.route_id = :route_id
                GROUP BY t.direction_id
            ) AS max_stops ON stop_times.trip_id = max_stops.trip_id
                AND stop_times.stop_sequence = max_stops.max_stop_sequence
            INNER JOIN trips ON stop_times.trip_id = trips.trip_id
            INNER JOIN stops ON stop_times.stop_id = stops.stop_id
            WHERE trips.route_id = :route_id
                AND stop_times.stop_sequence = max_stops.max_stop_sequence
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


    def get_offline_schedule(self, journey):

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
            departure_time = self.convert_time(departure_time)
            departure_time = self.format_time(departure_time)

            departure = {
                'line_name': route_name,
                'line_direction':  dir_name,
                'departure_time': departure_time
            }

            departures.append(departure)

        return departures


    def get_realtime_schedule(self, feed, target_stop):

        count = 0
        departures = []
        cur_timestamp = int(datetime.now().timestamp())

        for entity in feed.entity:

            if entity.HasField('trip_update'):

                for stop_time_update in entity.trip_update.stop_time_update:
                    stop_id = stop_time_update.stop_id
                    timestamp = stop_time_update.arrival.time
                    delay = stop_time_update.departure.delay

                    if (stop_id == target_stop and timestamp >= cur_timestamp):
                        route_id = entity.trip_update.trip.route_id
                        trip_id = entity.id

                        query_route = """SELECT route_short_name from routes where route_id = :route_id"""
                        route_short_name = self.query_db(query_route, {'route_id':route_id})
                        route_short_name = route_short_name[0][0]

                        # We first try to get the real terminus directly from gtfs data using the trip id
                        query_direction = """SELECT trip_headsign from trips where trip_id = :trip_id"""
                        trip_info = self.query_db(query_direction, {'trip_id':trip_id})

                        # But sometimes even if the trip id is 100% valid there is simply no reference about it in the gtfs db
                        # In such case we're forced to use the general (offline) terminus name which can differ from the real one
                        if trip_info:
                            trip_headsign = trip_info[0][0]
                        else:
                            direction_id = entity.trip_update.trip.direction_id
                            query_direction = """SELECT trip_headsign from trips where route_id = :route_id and direction_id = :direction_id limit 1"""
                            trip_info = self.query_db(query_direction, {'route_id':route_id, 'direction_id': direction_id})
                            trip_headsign = trip_info[0][0]

                        departure_time = datetime.fromtimestamp(timestamp)
                        departure_time = self.format_time(departure_time)
                        departures.append({
                            'line_name': route_short_name,
                            'line_direction': trip_headsign,
                            'departure_timestamp': timestamp,
                            'departure_time': departure_time
                        })

                        count += 1

                    # Fetch only the first 10 results
                    if count > 9:
                        break

        # Sort departures using timestamp (lowest to highest)
        departures.sort(key=lambda x: x["departure_timestamp"])

        return departures


    # Display theoretical hours if real time feed can't be fetched or is empty
    def select_schedule(self, journey, stop_id):

        feed = self.select_feed()

        if feed:
            schedule = self.get_realtime_schedule(feed, stop_id)
            is_realtime = True
        else:
            schedule = self.get_offline_schedule(journey)
            is_realtime = False

        return {'schedule': schedule, 'is_realtime': is_realtime}
