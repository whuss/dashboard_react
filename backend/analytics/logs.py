import os
from datetime import date
from typing import Optional

import pandas as pd

from db import LoggerPackage
from db import db, db_cached_permanent
from utils.date import start_of_day, end_of_day, date_range

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


#@db_cached
def error_heatmap_device(device: str, start_date: date, end_date: Optional[date] = None) -> pd.DataFrame:
    if end_date is None:
        end_date = date.today()

    data_list = list()
    for day in date_range(start_date, end_date, include_endpoint=True):
        data_list.append(get_daily_errors(device, day))
    error_heatmap = pd.concat(data_list, axis=0)
    return error_heatmap

# ----------------------------------------------------------------------------------------------------------------------
