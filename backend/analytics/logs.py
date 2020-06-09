import os
from datetime import date, timedelta
from typing import Optional

import pandas as pd

from db import LoggerPackage, Errors
from db import db, db_cached_permanent, db_cached
from utils.date import start_of_day, end_of_day, date_range

# ----------------------------------------------------------------------------------------------------------------------


@db_cached_permanent
def get_daily_crashes(device: str, day: date) -> pd.DataFrame:
    from sqlalchemy import Date
    since = start_of_day(day)
    until = end_of_day(day)
    lp = LoggerPackage

    query = db.session \
        .query(lp.timestamp.cast(Date).label('date'),
               db.func.count(lp.timestamp).label('crash_count')
               ) \
        .filter(lp.device == device) \
        .filter(lp.timestamp >= since) \
        .filter(lp.timestamp <= until) \
        .filter(lp.log_level == "CRITICAL") \
        .group_by('date')

    data = pd.DataFrame(query.all())
    if data.empty:
        return data

    return data

# ----------------------------------------------------------------------------------------------------------------------


@db_cached_permanent
def get_daily_errors(device: str, day: date) -> pd.DataFrame:
    from sqlalchemy import Date
    since = start_of_day(day)
    until = end_of_day(day)
    lp = LoggerPackage

    query = db.session \
        .query(lp.timestamp.cast(Date).label('date'),
               lp.filename,
               lp.line_number,
               db.func.count(lp.timestamp).label('error_count')
               ) \
        .filter(lp.device == device) \
        .filter(lp.timestamp >= since) \
        .filter(lp.timestamp <= until) \
        .filter(lp.log_level.in_(["ERROR", "CRITICAL"])) \
        .group_by(lp.filename) \
        .group_by(lp.line_number)
    data = pd.DataFrame(query.all())
    if data.empty:
        return data

    data['location'] = data.apply(
        lambda row: f"{os.path.basename(row['filename'])}:{row['line_number']}", axis=1)
    data = data.drop(columns=['filename', 'line_number'])
    return data

# ----------------------------------------------------------------------------------------------------------------------


@db_cached
def error_heatmap_device(device: str, start_date: date, end_date: Optional[date] = None) -> pd.DataFrame:
    if end_date is None:
        end_date = date.today()

    data_list = list()
    for day in date_range(start_date, end_date, include_endpoint=True):
        data_list.append(get_daily_errors(device, day))
    error_heatmap = pd.concat(data_list, axis=0)
    return error_heatmap

# ----------------------------------------------------------------------------------------------------------------------


@db_cached
def crash_heatmap_device(device: str, start_date: date, end_date: Optional[date] = None) -> pd.DataFrame:
    if end_date is None:
        end_date = date.today()

    data_list = list()
    for day in date_range(start_date, end_date, include_endpoint=True):
        data_list.append(get_daily_crashes(device, day))
    crash_heatmap = pd.concat(data_list, axis=0)
    return crash_heatmap

# ----------------------------------------------------------------------------------------------------------------------


@db_cached
def crash_restart_histogram(device: str, start_date: date, end_date: Optional[date] = None) -> pd.DataFrame:
    if end_date is None:
        end_date = date.today()

    crash_histogram = crash_heatmap_device(device, start_date, end_date)
    if crash_histogram.empty:
        crash_histogram = pd.DataFrame(columns=['date', 'crash_count'])

    restart_histogram = Errors.restart_histogram(device, start_of_day(start_date))
    restart_histogram = restart_histogram[restart_histogram.date <= end_date]

    if crash_histogram.empty and restart_histogram.empty:
        return pd.DataFrame()

    if crash_histogram.empty:
        combined_histogram = restart_histogram
        combined_histogram.loc[:, 'crash_count'] = 0
    elif restart_histogram.empty:
        combined_histogram = crash_histogram
        combined_histogram.loc[:, 'restart_count'] = 0
    else:
        combined_histogram = crash_histogram.merge(restart_histogram, on='date', how='outer').fillna(value=0)

    # compute string of the end of the day for url creation
    def _end_of_day(row):
        return (row.date + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

    combined_histogram['end_of_day'] = combined_histogram.apply(_end_of_day, axis=1)
    return combined_histogram.set_index(['date'])

# ----------------------------------------------------------------------------------------------------------------------
