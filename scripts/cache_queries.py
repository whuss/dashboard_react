#! /usr/bin/env python
import signal
import traceback
import os
from typing import Optional
from datetime import datetime, date, timedelta, time
import click
from plumbum import colors
from plumbum.cli.terminal import get_terminal_size
import pandas as pd

from app import db
from db import query_cache, Dashboard, DataFramePackage, DeviceDataFramePackage, Errors
from analytics.sensors import get_sensor_data
from analytics.scenes import get_scene_durations
from utils.date import parse_date, date_range, start_of_day
from dataclasses import dataclass

# ----------------------------------------------------------------------------------------------------------------------


@dataclass
class Query:
    day: Optional[date]
    device: str
    name: str

# ----------------------------------------------------------------------------------------------------------------------


def hline():
    width, height = get_terminal_size(default=(80, 25))
    print(width * u'\u2500')

# ----------------------------------------------------------------------------------------------------------------------


def get_devices():
    def _is_ptl(device):
        if not "PTL" in device:
            return False
        if device == "PTL_DEFAULT" or device == "PTL_UNIT_TEST":
            return False

        return True
    return [device for device in Dashboard().devices() if _is_ptl(device)]

# ----------------------------------------------------------------------------------------------------------------------


def clear_device_query(query: str) -> None:
    try:
        num_packages = db.session.query(DeviceDataFramePackage) \
            .filter(DeviceDataFramePackage.query == query) \
            .delete()
        db.session.commit()
        print(f"Number of cache entries deleted: {num_packages}.")
    except:
        db.session.rollback()
        print(f"Clearing cache failed. Rollback transaction.")

# ----------------------------------------------------------------------------------------------------------------------


def update_scene_data(query: str, device: str, start_date: date, end_date: date) -> None:
    if query == "scene_durations":
        data = get_scene_durations(device, start_date, end_date)
    elif query == "error_restart_histogram":
        data = Errors().crash_restart_histogram(device, start_of_day(start_date))
    else:
        raise ValueError(f"Unknown query: {query}.")
    # print(data)
    data_package = DeviceDataFramePackage(device=device, query=query, data=data)
    db.session.add(data_package)
    db.session.commit()

# ----------------------------------------------------------------------------------------------------------------------


def cache_sensor_data(device: str, data_date: date):
    since = datetime.combine(data_date, time(0))
    until = datetime.combine(data_date, time(23, 59, 59))
    data = get_sensor_data(device, (since, until), rule="1s")
    data_package = DataFramePackage(device=device, date=data_date, query="sensor_data", data=data)
    db.session.add(data_package)
    db.session.commit()

# ----------------------------------------------------------------------------------------------------------------------


@click.group()
def main():
    pass

# ----------------------------------------------------------------------------------------------------------------------


@click.command(name="init", help="Create database tables")
def initialize_cache():
    click.confirm("Create database tables for query cache?", abort=True)
    db.create_all(bind='cache')

# ----------------------------------------------------------------------------------------------------------------------


@click.command(name="clear", help="clear all data from cache")
def clear_cache():
    click.confirm("Delete all cached queries?", abort=True)
    try:
        num_packages = db.session.query(DataFramePackage).delete()
        db.session.commit()
        print(f"Number of cache entries deleted: {num_packages}.")
    except:
        db.session.rollback()
        print(f"Clearing cache failed. Rollback transaction.")

# ----------------------------------------------------------------------------------------------------------------------


@click.command(name="update", help="update query cache")
@click.argument("start_date", type=str)
def update_cache(start_date: date):
    query_keys = ["scene_durations", "error_restart_histogram"]
    devices = get_devices()

    start_date = parse_date(start_date)
    end_date: date = date.today()

    number_of_queries = len(query_keys) * len(devices)
    progress = 1

    print(f"Cache queries for dates: {start_date} - {end_date}.")
    print(f"Number of queries: {number_of_queries}")
    queries = list()
    for device in devices:
        for key in query_keys:
            queries.append(Query(None, device, key))

    hline()

    for query in query_keys:
        clear_device_query(query)

    for query in queries:
        print(colors.bold | f"[{progress:>4}/{len(queries)}]", end=" ")
        print(f"Fetch {query.device:<13} {query.name}...", end=" ", flush=True)
        try:
            update_scene_data(query.name, query.device, start_date, end_date)
            print(colors.green | "done")
        except:
            print(colors.red | "failed")
            hline()
            print(traceback.format_exc())
            hline()
        progress += 1

# ----------------------------------------------------------------------------------------------------------------------


@click.command(name="fill", help="fill query cache")
@click.argument("start_date", type=str)
def fill_cache(start_date: date):
    query_keys = ["sensor_data"]
    devices = get_devices()

    start_date = parse_date(start_date)
    end_date: date = date.today()

    number_of_days = (end_date - start_date).days
    number_of_queries = number_of_days * len(devices)
    progress = 1

    print(f"Cache queries for dates: {start_date} - {end_date}.")
    print(f"Number of queries: {number_of_queries}")

    queries = list()
    for day in date_range(start_date, end_date):
        for device in devices:
            for key in query_keys:
                if not query_cache(device, day, key):
                    queries.append(Query(day, device, key))
    print(f"Number of cached queries: {number_of_queries - len(queries)}")

    hline()

    for query in queries:
        day_str = query.day.strftime('%Y-%m-%d')
        print(colors.bold | f"[{progress:>4}/{len(queries)}]", end=" ")
        print(f"Fetch {day_str}, {query.device:<13} ...", end=" ", flush=True)
        try:
            cache_sensor_data(query.device, query.day)
            print(colors.green | "done")
        except:
            print(colors.red | "failed")
        progress += 1

# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------


main.add_command(initialize_cache)
main.add_command(update_cache)
main.add_command(fill_cache)
main.add_command(clear_cache)

# ----------------------------------------------------------------------------------------------------------------------


# pylint: disable=unused-argument
def signal_handler(sig, frame):
    print('You pressed Ctrl+C! Terminate ...')
    os.kill(os.getpid(), signal.SIGKILL)

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()

# ----------------------------------------------------------------------------------------------------------------------


