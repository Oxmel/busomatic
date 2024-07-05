#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Name : busquery.py

import os
import sqlite3

# The sqlite database is not located in this folder or any subfolder
# So we need to manually construct the full path to the db
# https://stackoverflow.com/a/14150750
path_to_db = os.path.abspath(__file__ + '/../../db/t2c-gtfs.db')
conn = sqlite3.connect(path_to_db)
cursor = conn.cursor()


trip_data = ({
    "route_id": "",
    "direction_id": "",
    "stop_id": "",
    "cur_date": "2024-07-04",
    "cur_day": "thursday",
    "cur_time": "16:00:00",
    "weekday": 3
})


# Original GTFS contains a lot of special lines we don't need
# So we filter lines by name and size to get regular services only
def get_lines():

    cursor.execute("""

        SELECT route_id,
          route_long_name
        FROM routes
        WHERE route_long_name LIKE 'T%'
          OR route_long_name LIKE 'L%'
          AND length(route_long_name) < 9
        ORDER BY route_short_name + 0 ASC

    """)

    response = cursor.fetchall()
    return response


def get_directions(line_id):

    trip_data['route_id'] = line_id

    cursor.execute("""

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

    """, trip_data)

    response = cursor.fetchall()
    return response


def get_stops(direction_id):

    trip_data['direction_id'] = direction_id

    cursor.execute("""

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

    """, trip_data)

    response = cursor.fetchall()
    return response


def get_departures(stop_id):

    trip_data['stop_id'] = stop_id

    cursor.execute("""

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

    """, trip_data)

    response = cursor.fetchall()
    return response
