#! /usr/bin/env python
import itertools
import os
import signal
import traceback
from datetime import date
from functools import reduce
from typing import Optional

import click
import requests
from dataclasses import dataclass
from plumbum import colors
from plumbum.cli.terminal import get_terminal_size

from analytics.connection import connection_data_per_day
from analytics.scenes import get_scene_durations
from analytics.sensors import get_sensor_data_for_day
from analytics.logs import get_daily_errors
from app import db
from db import Dashboard, CachePackage, CacheDeviceDatePackage, Errors, PresenceDetectorStatistics
from utils.date import parse_date, date_range, start_of_day


# from joblib import Parallel, delayed

BACKEND_URL = os.getenv("BACKEND", "http://127.0.0.1:5000")

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
        num_packages = db.session.query(CachePackage) \
            .filter(CachePackage.query == query) \
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
    elif query == "connection_data":
        data = connection_data_per_day(device, start_date, end_date)
    elif query == "on_off_cycle_count":
        data = PresenceDetectorStatistics.on_off_cycle_count(device, start_date)
    elif query == "error_heatmap_device":
        data = Errors().error_heatmap_device(device, start_of_day(start_date))
    else:
        raise ValueError(f"Unknown query: {query}.")

# ----------------------------------------------------------------------------------------------------------------------


def cache_sensor_data(device: str, data_date: date):
    _ = get_sensor_data_for_day(device, data_date, rule="1s")
    _ = get_daily_errors(device, data_date)

# ----------------------------------------------------------------------------------------------------------------------


@click.group()
def main():
    pass

# ----------------------------------------------------------------------------------------------------------------------


@click.command(name="init", help="Create database tables")
@click.option('-y', '--yes', is_flag=True)
def initialize_cache(yes):
    if not yes:
        click.confirm("Create database tables for query cache?", abort=True)
    db.create_all(bind='cache')

# ----------------------------------------------------------------------------------------------------------------------


@click.command(name="clear", help="clear all data from cache")
def clear_cache():
    click.confirm("Delete all cached queries?", abort=True)
    try:
        num_packages = db.session.query(CacheDeviceDatePackage).delete()
        db.session.commit()
        print(f"Number of cache entries deleted: {num_packages}.")
    except:
        db.session.rollback()
        print(f"Clearing cache failed. Rollback transaction.")

# ----------------------------------------------------------------------------------------------------------------------


plot_list = {"PlotCrashes": {},
             "PlotSceneDurations": {},
             "PlotOnOffCycles": {},
             # "PlotErrors": {}, # uses permanent cache
             "PlotConnection": {},
             "PlotKeyboard": {},
             "PlotKeypress": {},
             "PlotMouse": {},
             # "PlotClusteringInputDistribution":
             #     {"columns":
             #         ["key_press_count",
             #          "delete_press_count",
             #          "enter_press_count",
             #          "shift_press_count",
             #          "space_press_count",
             #          "press_pause_count",
             #          "pause_length",
             #          "keystroke_time",
             #          "press_to_press_time",
             #          "click_count",
             #          "double_click_count",
             #          "rotation_distance",
             #          "rotation_speed",
             #          "event_count",
             #          "gesture_distance",
             #          "gesture_speed",
             #          "gesture_deviation",
             #          "gesture_duration_seconds"],
             #      "transformation":
             #          ["none",
             #           "power transform"]
             #      },
             "PlotClusteringScatterPlot":
                 {"x_axis":
                      ["d_0", "d_1", "d_2", "d_3", "d_4", "d_5"],
                  "y_axis":
                      ["d_0", "d_1", "d_2", "d_3", "d_4", "d_5"]
                  },
             "PlotClusteringFrequency": {},
             "PlotClusteringTimeline": {},
             "PlotPowerTimeline": {}
             }

# ----------------------------------------------------------------------------------------------------------------------


def get_devices():
    base_url = f"{BACKEND_URL}/backend"

    r = requests.get(base_url + "/devices")
    return r.json()

# ----------------------------------------------------------------------------------------------------------------------

@dataclass
class CacheQueries:
    number_of_queries: int
    progress: int
    plot_name: str
    plot_parameters: dict

# ----------------------------------------------------------------------------------------------------------------------


def cache_functions():
    devices = get_devices()

    parameter_list = [[len(l) for l in parameters.values()] for parameters in plot_list.values()]
    parameter_list = [reduce(lambda x, y: x*y, pl, 1) for pl in parameter_list]

    number_of_queries = len(devices) * sum(parameter_list)
    progress = 1

    for plot in plot_list.keys():
        parameter_dict = plot_list[plot]
        parameter_names = list(parameter_dict.keys())
        if parameter_dict == {}:
            for device in devices:
                plot_parameters = {'device': device}
                yield CacheQueries(number_of_queries, progress, plot, plot_parameters)
                progress += 1
        else:
            cartesian_product = list(itertools.product(*parameter_dict.values()))
            for parameter_values in cartesian_product:
                for device in devices:
                    plot_parameters = {k: v for k, v in zip(parameter_names, parameter_values)}
                    plot_parameters['device'] = device
                    yield CacheQueries(number_of_queries, progress, plot, plot_parameters)
                    progress += 1

# ----------------------------------------------------------------------------------------------------------------------


def backend_request(query: CacheQueries):
    base_url = f"{BACKEND_URL}/backend"

    plot_parameters = query.plot_parameters
    plot_name = query.plot_name
    progress = query.progress
    number_of_queries = query.number_of_queries

    #print(colors.bold | f"[{progress:>4}/{number_of_queries}]", end=" ")
    print(f"[{progress:>4}/{number_of_queries}]", end = " ")
    print(f"Fetch {plot_parameters['device']:<13} {plot_name} {plot_parameters} ...", end=" ", flush=True)
    try:
        r = requests.post(base_url + "/plot/" + plot_name, json=plot_parameters)
        result = r.json()
        if 'error' in result:
            print(result['error'])
            #print(colors.red | "failed")
            print("failed")
        else:
            #print(colors.green | "done")
            print("done")
    except:
        #print(colors.red | "failed")
        print("failed")
        hline()
        print(traceback.format_exc())
        hline()

# ----------------------------------------------------------------------------------------------------------------------


@click.command(name="update", help="update query cache")
def update_cache():
    #Parallel(n_jobs=4)(delayed(backend_request)(query) for query in cache_functions())
    for query in cache_functions():
        backend_request(query)

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


