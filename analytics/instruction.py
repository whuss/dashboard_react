from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import pandas as pd

from app import db, app
from db import InstructionPackage, VersionPackage
from utils.interval import TimeInterval, Interval

# ----------------------------------------------------------------------------------------------------------------------


def parse_interval(interval):
    if isinstance(interval, Interval):
        return interval
    if isinstance(interval, tuple):
        if len(interval) == 2 and isinstance(interval[0], datetime) and isinstance(interval[1], datetime):
            begin, end = interval
            return TimeInterval(begin, end)
    if isinstance(interval, pd.core.Series):
        return interval

    raise TypeError(f"Incorrect type for parameter interval: {interval}.")

# ----------------------------------------------------------------------------------------------------------------------


def expand_mode_dataframe(data, since: datetime, until: datetime, column_name: str):
    """Duplicate last value with timestamp set to until."""
    if data.empty:
        data = pd.DataFrame({"timestamp": [since, until], "status": ["OFF", "OFF"]}).set_index('timestamp')
    else:
        # get last data point
        last_value = data.iloc[-1].copy()
        # change timestamp
        last_value.name = until

        first_value = last_value.copy()
        first_value.name = since
        first_value.status = "OFF"
        data = pd.concat([pd.DataFrame([first_value]),
                          data,
                          pd.DataFrame([last_value])],
                         axis=0)[['status']]

        # remove duplicate index entries
        data = data.reset_index()\
            .drop_duplicates(subset=['index']) \
            .set_index('index')

    def on_off(value):
        if value == "OFF":
            return 0
        elif value == "ON":
            return 1
        raise ValueError(f"data {value} is not in ['ON', 'OFF']")

    data = data.applymap(on_off)

    # resample data
    data = data.resample("1s").ffill()
    data = data.rename(columns=dict(status=column_name))

    return data

# ----------------------------------------------------------------------------------------------------------------------


def get_mode_data_raw(device: str, interval) -> pd.DataFrame:
    """Returns dataframe of all instructions that changed the ptl running mode in the given interval.

    @parameter: device
        Device name of a PTL

    @parameter: interval
        A time interval. Either a tuple of two date objects, or an object with properties 'begin' and 'end'
        which return date objects.

    @returns: a pandas dataframe with three data columns 'timestamp', 'target' and 'status'.

        timestamp: contains datetime objects
        target: contains strings in the set {'POWER_PRESENCE', 'POWER_MANUAL', 'LIGHT_SHOWER', 'TASK_VERT', 'TASK_HORI'}
        status: contains strings in the set {'OFF', 'ON'}

        the returned dataframe is sorted by the timestamp column.
    """

    interval = parse_interval(interval)
    since, until = interval.begin, interval.end

    # Gather instructions
    ip = InstructionPackage

    # Find the timestamp of the last instruction before the selected time interval
    query_last_timestamp = db.session.query(db.func.max(ip.timestamp).label('timestamp')) \
        .filter(ip.instruction == "MODE") \
        .filter(ip.device == device) \
        .filter(ip.timestamp < since)

    sq_last_timestamp = query_last_timestamp.subquery()

    # Get the last recorded sensor value before the selected time interval
    query_last_mode = db.session.query(ip.source, ip.target, ip.value) \
        .filter(ip.device == device) \
        .filter(ip.timestamp == sq_last_timestamp.c.timestamp)

    first_mode = query_last_mode.first()

    # Get instruction values in the selected time interval
    query = db.session.query(ip.source, ip.target, ip.value, ip.timestamp) \
        .filter(ip.instruction == "MODE") \
        .filter(ip.device == device) \
        .filter(ip.timestamp >= since) \
        .filter(ip.timestamp <= until) \
        .order_by(ip.timestamp)

    # Create data frame
    if first_mode:
        data_since = pd.DataFrame({"timestamp": [since],
                                   "source": first_mode.source,
                                   "target": first_mode.target,
                                   "value": first_mode.value})
    else:
        data_since = pd.DataFrame()
    data_between = pd.DataFrame(query.all())

    data_instructions = pd.concat([data_since, data_between], axis=0) \
        .rename(columns=dict(value="status"))

    # Remove "None@" from column source
    def format_source(source):
        try:
            return source.split("@")[1]
        except IndexError:
            return source
    data_instructions.source = data_instructions.source.apply(format_source)

    # Distinguish between manual power commands and power commands based on presence detection.
    def power(row):
        if row['target'] == "POWER":
            if row['source'] == "Lullaby":
                return "POWER_PRESENCE"
            if row['source'] == "DataDock":
                return "POWER_MANUAL"

            raise ValueError(f"Unknown combination of source={row['source']} and target={row['target']}.")

        return row['target']

    data_instructions.target = data_instructions.apply(power, axis=1)

    # round timestamps to the nearest second
    #data_instructions.timestamp = data_instructions.timestamp.apply(lambda t: t.round('1s'))

    # select columns
    data_instructions = data_instructions[['timestamp', 'target', 'status']]

    # find all restarts in the selected time interval
    vp = VersionPackage
    query_restart = db.session.query(vp.timestamp) \
        .filter(vp.device == device) \
        .filter(vp.timestamp >= since) \
        .filter(vp.timestamp <= until) \
        .order_by(vp.timestamp)

    data_restart = pd.DataFrame(query_restart.all())
    data_restart['target'] = "RESTART"
    data_restart['status'] = "ON"

    # combine instructions and restarts
    data = pd.concat([data_instructions, data_restart], axis=0)

    return data.sort_values(by="timestamp").set_index("timestamp")

# ----------------------------------------------------------------------------------------------------------------------


def get_mode_data_version1(device, interval, rule: str = "1Min") -> pd.DataFrame:
    data = get_mode_data_raw(device, interval)
    interval = parse_interval(interval)
    since, until = interval.begin, interval.end

    columns = [
        expand_mode_dataframe(data[data.target == 'POWER_MANUAL'], since, until, column_name="power_manual"),
        expand_mode_dataframe(data[data.target == 'POWER_PRESENCE'], since, until, column_name="presence"),
        expand_mode_dataframe(data[data.target == 'TASK_VERT'], since, until, column_name="vertical"),
        expand_mode_dataframe(data[data.target == 'TASK_HORI'], since, until, column_name="horizontal"),
        expand_mode_dataframe(data[data.target == 'LIGHT_SHOWER'], since, until, column_name="light_shower"),
        expand_mode_dataframe(data[data.target == 'SETTINGS'], since, until, column_name="settings")
        ]

    return pd.concat(columns, axis=1)

# ----------------------------------------------------------------------------------------------------------------------


def get_mode_data_version2(device: str, interval) -> pd.DataFrame:
    data_raw = get_mode_data_raw(device, interval)
    interval = parse_interval(interval)
    since, until = interval.begin, interval.end

    def filter_target_column(data: pd.DataFrame, target: str):
        return data[data.target == target].drop(columns='target') \
            .rename(columns=dict(status=target))

    # todo add "SETTINGS" and "POWER_MANUAL"
    instruction_targets = ['POWER_PRESENCE', 'POWER_MANUAL', 'LIGHT_SHOWER', 'TASK_VERT', 'TASK_HORI', 'SETTINGS']

    split_data = [filter_target_column(data_raw, target) for target in instruction_targets]

    from functools import reduce
    merged_data = reduce(lambda a, b: pd.merge(a, b, how='outer', on='timestamp'), split_data)
    return merged_data.sort_values(by="timestamp")

# ----------------------------------------------------------------------------------------------------------------------


@dataclass
class State:
    power: str
    mode: str
    settings: str

# ----------------------------------------------------------------------------------------------------------------------


def state_transitions(state: State, transition) -> State:
    new_state: State = State(state.power, state.mode, state.settings)
    if transition.target in ["POWER_PRESENCE", "POWER_MANUAL"]:
        new_state.power = transition.status
        return new_state

    if transition.target in ["LIGHT_SHOWER", "TASK_HORI", "TASK_VERT"]:
        new_state.power = "ON"
        new_state.settings = "OFF"
        if transition.status == "ON":
            new_state.mode = transition.target
        elif transition.status == "OFF":
            new_state.mode = "AUTO"
        else:
            raise ValueError(f"Unknown transition: state={(state.power, state.mode, state.settings)}, "
                             f"transition={(transition.target, transition.value)}")
        return new_state

    if transition.target == "SETTINGS":
        new_state.settings = transition.status
        return new_state

    if transition.target == "RESTART":
        new_state.mode = "AUTO"
        new_state.settings = "OFF"
        return new_state

    raise ValueError(f"Unknown transition: state={(state.power, state.mode, state.settings)}, "
                     f"transition={(transition.target, transition.value)}")

# ----------------------------------------------------------------------------------------------------------------------


def get_mode_data(device: str, interval) -> pd.DataFrame:
    data = get_mode_data_raw(device, interval)
    interval = parse_interval(interval)
    since, until = interval.begin, interval.end

    data['power'] = pd.NaT
    data['mode'] = pd.NaT
    data['settings'] = pd.NaT

    # Set initial state
    first_timestamp = data.index.min()
    data.loc[first_timestamp, 'power'] = "OFF"
    data.loc[first_timestamp, 'mode'] = "AUTO"
    data.loc[first_timestamp, 'settings'] = "OFF"

    # Apply state transition automaton
    state = None
    for index, row in data.iterrows():
        if not state:
            # the state is already set for the first row
            state = State(row['power'], row['mode'], row['settings'])
            continue

        # compute state transition
        transition = row
        state = state_transitions(state, transition)

        # update state in current row
        row['power'] = state.power
        row['mode'] = state.mode
        row['settings'] = state.settings

    return data

# ----------------------------------------------------------------------------------------------------------------------
