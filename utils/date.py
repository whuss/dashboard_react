from datetime import datetime, timedelta, date, time
from typing import Union
import humanfriendly

# ----------------------------------------------------------------------------------------------------------------------


def parse_date(timestamp: Union[datetime, str]) -> datetime:
    if isinstance(timestamp, datetime):
        return timestamp
    try:
        return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.strptime(timestamp, '%Y-%m-%d %H:%M')

# ----------------------------------------------------------------------------------------------------------------------


def format_time_span(td: timedelta) -> str:
    seconds = td.seconds
    minutes = seconds // 60
    seconds = seconds % 60
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# ----------------------------------------------------------------------------------------------------------------------


def format_timespan_sloppy(td: timedelta) -> str:
    if td < timedelta(minutes=1):
        return f"{int(td.total_seconds())} seconds"
    if td < timedelta(hours=1):
        return humanfriendly.format_timespan(td, max_units=1)

    return humanfriendly.format_timespan(td, max_units=2)

# ----------------------------------------------------------------------------------------------------------------------


def parse_date(date_str: str) -> date:
    return datetime.strptime(date_str, "%Y-%m-%d").date()

# ----------------------------------------------------------------------------------------------------------------------


def date_range(start_date: date, end_date: date):
    one_day = timedelta(days=1)
    current_date = start_date
    while current_date < end_date:
        yield current_date
        current_date += one_day

# ----------------------------------------------------------------------------------------------------------------------


def start_of_day(day: date) -> datetime:
    return datetime.combine(day, time())

# ----------------------------------------------------------------------------------------------------------------------


def end_of_day(day: date) -> datetime:
    return datetime.combine(day, time(23, 59, 59, 999999))

# ----------------------------------------------------------------------------------------------------------------------
