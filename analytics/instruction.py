from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from enum import Enum
from typing import Optional

import pandas as pd

from app import db, app
from db import InstructionPackage
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

    # resample data
    data = data.resample("1s").ffill()
    data = data.rename(columns=dict(status=column_name))
    return data

# ----------------------------------------------------------------------------------------------------------------------


def get_mode_data(device, interval, rule: str = "1Min") -> pd.DataFrame:
    interval = parse_interval(interval)
    since, until = interval.begin, interval.end

    ip = InstructionPackage

    # Find the timestamp of the last instruction before the selected time interval
    query_last_timestamp = db.session.query(db.func.max(ip.timestamp).label('timestamp')) \
        .filter(ip.instruction == "MODE") \
        .filter(ip.device == device) \
        .filter(ip.timestamp < since)

    sq_last_timestamp = query_last_timestamp.subquery()

    # Get the last recorded sensor value before the selected time interval
    query_last_mode = db.session.query(ip.target, ip.value) \
        .filter(ip.device == device) \
        .filter(ip.timestamp == sq_last_timestamp.c.timestamp)

    first_mode = query_last_mode.first()

    # Get instruction values in the selected time interval
    query = db.session.query(ip.target, ip.value, ip.timestamp) \
        .filter(ip.instruction == "MODE") \
        .filter(ip.device == device) \
        .filter(ip.timestamp >= since) \
        .filter(ip.timestamp <= until) \
        .order_by(ip.timestamp)

    # Create data frame
    data_since = pd.DataFrame({"timestamp": [since], "target": first_mode.target, "value": first_mode.value})
    data_between = pd.DataFrame(query.all())

    data = pd.concat([data_since, data_between], axis=0) \
        .rename(columns=dict(value="status")) \
        .set_index("timestamp") \
        .sort_index()

    columns = [
        expand_mode_dataframe(data[data.target == 'POWER'], since, until, column_name="power"),
        expand_mode_dataframe(data[data.target == 'TASK_VERT'], since, until, column_name="vertical"),
        expand_mode_dataframe(data[data.target == 'TASK_HORI'], since, until, column_name="horizontal"),
        expand_mode_dataframe(data[data.target == 'LIGHT_SHOWER'], since, until, column_name="light_shower"),
        expand_mode_dataframe(data[data.target == 'SETTINGS'], since, until, column_name="settings")
        ]

    return pd.concat(columns, axis=1)

# ----------------------------------------------------------------------------------------------------------------------
