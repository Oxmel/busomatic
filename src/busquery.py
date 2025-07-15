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

        for departure in departures:
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

            departure_time = self.format_time(time_obj)
            realtime_schedule.append({
                'line_name': departure['route_name'],
                'line_direction': departure['direction_name'],
                'departure_time': departure_time
            })

        return realtime_schedule


    def get_offline_schedule(self, departures):

        schedule = []

        for departure in departures:
            scheduled_time = departure['scheduled_time']
            time_obj = self.convert_time(scheduled_time)
            departure_time = self.format_time(time_obj)
            schedule.append({
                'line_name': departure['route_name'],
                'line_direction': departure['direction_name'],
                'departure_time': departure_time
            })

        return schedule

    # Display theorical hours if real time feed can't be fetched or is empty
    def select_schedule(self, journey, stop_id):

        departures = self.get_departures(journey)
        feed = self.select_feed()

        if feed:
            schedule = self.get_realtime_schedule(feed, stop_id, departures)
            is_realtime = True
        else:
            schedule = self.get_offline_schedule(departures)
            is_realtime = False

        return {'schedule': schedule, 'is_realtime': is_realtime}
