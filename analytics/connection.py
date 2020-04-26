from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional

import pandas as pd

from db import db, DeadManPackage, db_cached
from utils.interval import find_intervals
from utils.date import start_of_day, end_of_day

# ----------------------------------------------------------------------------------------------------------------------


def _find_connection_intervals(data, max_delay: timedelta):
    colors = ['#a1eca4', '#ff0000']  # [connected, disconnected]

    # compute the time difference between two consecutive rows
    data['delay'] = data.timestamp.diff()
    # The first row for each device has no 'delay' value.
    # We assume this is the start of a connected interval.
    # To do this we set the delay to be bigger than the threshold
    # for data loss
    data = data.fillna(2 * max_delay)
    # A data loss happened, if the delay is bigger than a threshold
    # If the row 'connected' contains 1 then no data loss happened at this time
    data['data_loss'] = (data.delay <= max_delay).astype(int)
    # compute the difference of consecutive data_loss values to see where
    # the connection status changed
    data['keep_row'] = data.data_loss.diff(periods=-1)
    # We merge intervals of consecutive 'data loss' or 'connection' intervals by
    # keeping only rows where the value of 'keep_rows' is not zero
    data = data[data.keep_row != 0.0]
    # the timestamp row now marks the beginning of an interval where
    # the connection status did not change.
    data = data.rename(columns=dict(timestamp='begin'))
    # compute the duration of each interval
    data['duration'] = data.begin.diff(periods=-1).abs()
    data['end'] = data.begin + data.duration
    data['connected'] = 1 - data.data_loss
    data = data.drop(columns=['delay', 'keep_row', 'data_loss'])
    data['color'] = colors[0]
    data.loc[data.connected == 0, 'color'] = colors[1]
    data = data.dropna()

    return data


# ----------------------------------------------------------------------------------------------------------------------


@db_cached
def _connection_for_device_raw(device: str) -> pd.DataFrame:
    dmp = DeadManPackage
    query = db.session.query(dmp.timestamp) \
        .filter(dmp.device == device)

    return pd.DataFrame(query.all())


# ----------------------------------------------------------------------------------------------------------------------


@db_cached
def _connection_for_device(device: str, max_delay: timedelta) -> pd.DataFrame:
    raw_data = _connection_for_device_raw(device)
    if raw_data.empty:
        return raw_data
    return _find_connection_intervals(raw_data, max_delay)

# ----------------------------------------------------------------------------------------------------------------------


def connection(device: str, start_date: date, end_date: date,
               max_delay: timedelta = timedelta(minutes=2), cut_intervals=False) -> pd.DataFrame:
    begin = start_of_day(start_date)
    end = end_of_day(end_date)
    fully_unconnected = pd.DataFrame(dict(begin=begin, end=end, duration=end-begin, connected=0, color=['#ff0000']))

    data = _connection_for_device(device, max_delay=max_delay)
    if data.empty:
        return fully_unconnected

    data = data[(begin <= data.end) & (data.begin <= end)]
    if data.empty:
        return fully_unconnected

    if cut_intervals:
        data.begin = data.begin.apply(lambda dt: max(begin, dt))
        data.end = data.end.apply(lambda dt: min(end, dt))
        # fix duration of cut intervals
        data.duration = data.end - data.begin

    end_of_last_interval = data.iloc[-1].end
    # Fill the hole at the end of the time interval, if there is no connection at the end
    if data.iloc[-1].connected == 1 and end_of_last_interval < end:
        unconnected = dict(begin=end_of_last_interval, end=end, duration=end-begin, connected=0, color=['#ff0000'])
        data = data.append(pd.DataFrame(unconnected))

    return data.reset_index(drop=True)

# ----------------------------------------------------------------------------------------------------------------------


def connection_timeseries(device: str, start_date: date, end_date: date,
                          max_delay: timedelta = timedelta(minutes=2)) -> pd.DataFrame:
    data_interval = connection(device, start_date, end_date, max_delay, cut_intervals=True)
    if data_interval.empty:
        return pd.DataFrame()

    data = data_interval[['begin', 'connected']]

    # Add a data row for the end of the time interval
    # To make sure the timeseries goes until the end.
    connected = data.iloc[-1].connected
    return data.append(pd.DataFrame(dict(begin=[end_of_day(end_date)], connected=[connected]))) \
        .rename(columns=dict(begin='timestamp')) \
        .set_index('timestamp') \
        .resample('1s') \
        .ffill()

# ----------------------------------------------------------------------------------------------------------------------
