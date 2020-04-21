from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TypeVar, Generic, Union

import pandas as pd
from pandas.core.series import Series

# ----------------------------------------------------------------------------------------------------------------------


# Type of interval boundaries, needs to support arithmetic and comparisons.
T = TypeVar('T')

# ----------------------------------------------------------------------------------------------------------------------


@dataclass
class Interval(Generic[T]):
    begin: T
    end: T

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def length(self):
        return self.end - self.begin

# ----------------------------------------------------------------------------------------------------------------------


TimeInterval = Interval[datetime]

# ----------------------------------------------------------------------------------------------------------------------


def is_intersecting(a: Union[Interval[T], Series],
                    b: Union[Interval[T], Series]) -> bool:
    # we assume a begins before b, otherwise swap the intervals
    if a.begin > b.begin:
        a, b = b, a

    return a.end >= b.begin

# ----------------------------------------------------------------------------------------------------------------------


class IntervalGenerator:
    def __init__(self, intervals):
        self.generator = intervals.iterrows()

    def next(self):
        try:
            return next(self.generator)[1]
        except StopIteration:
            return None

# ----------------------------------------------------------------------------------------------------------------------


def intersect_intervals(intervals_1, intervals_2):
    intersections = []
    generator_1 = IntervalGenerator(intervals_1)
    generator_2 = IntervalGenerator(intervals_2)

    interval_1 = generator_1.next()
    interval_2 = generator_2.next()
    while True:
        if interval_1 is None or interval_2 is None:
            return pd.DataFrame(intersections, columns=["begin", "end"])

        if not is_intersecting(interval_1, interval_2):
            if interval_1.begin < interval_2.begin:
                interval_1 = generator_1.next()
            else:
                interval_2 = generator_2.next()
            continue

        # intervals intersect

        if interval_1.begin <= interval_2.begin:
            if interval_1.end <= interval_2.end:
                # interval_1:    >----------------------<
                # interval_2:           >---------------------<
                # intersection:         >---------------<
                intersections.append((interval_2.begin, interval_1.end))
                interval_1 = generator_1.next()
            else:
                # interval_1:    >----------------------<
                # interval_2:           >----------<
                # intersection:         >----------<
                intersections.append((interval_2.begin, interval_2.end))
                interval_2 = generator_2.next()
        else:
            if interval_1.end >= interval_2.end:
                # interval_1:           >---------------------<
                # interval_2:    >----------------------<
                # intersection:         >---------------<
                intersections.append((interval_1.begin, interval_2.end))
                interval_2 = generator_2.next()
            else:
                # interval_1:           >----------<
                # interval_b:    >----------------------<
                # intersection:         >----------<
                intersections.append((interval_1.begin, interval_1.end))
                interval_1 = generator_1.next()

# ----------------------------------------------------------------------------------------------------------------------


def remove_short_intervals(intervals, length: timedelta):
    """Remove all intervals that are shorter than 'length'."""
    return intervals[intervals.end - intervals.begin > length]

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



def find_intervals(data: pd.DataFrame) -> pd.DataFrame:
    """Compute consecutive time intervals in a pandas data frame representing a timeseries.

    A new interval is assumed to start if the delay between to consecutive timestamps is bigger than
    1 second, or if the next row is on the following day.

    @parameter data:
        Data is assumed have a datetime column named 'timestamp', and it should be sorted by this columns.

        All other columns are ignored, and the data for the first element of each interval are returned unchanged.

    @returns a pandas dataframe with the columns 'begin', 'end', 'duration' where
        begin: datetime is the start time of each interval
        end: datetime is the end time of each interval
        duration: timedelta is the duration of each interval
    """
    if data.empty:
        return pd.DataFrame(columns=['begin', 'end', 'duration'])

    # The minimal length of an interval.
    # All delays bigger than this are assumed to start a new interval
    min_timedelta = timedelta(seconds=1)

    # compute the time difference between a row and the previous row grouped per day.
    # That means the time of the last data row of each day is not subtracted
    # from the time of the first data row of the next day, and the delay for
    # the first row of each day is set to NaT
    data.loc[:, 'delay'] = data.groupby([data.timestamp.dt.date]).timestamp.diff()

    # When ever the delay is bigger than min_timedelta a new interval starts
    data.loc[:, 'new_interval'] = (data.delay > min_timedelta).astype(int)
    # When delay is NaT this also means the start of a new interval.
    data.loc[data.delay.isna(), 'new_interval'] = 1

    # A row is the endpoint of an interval, when the the value of 'new_interval'
    # differs from the previous row.
    #
    # interval_endpoint == 1.0 means the start of an interval
    # interval_endpoint == -1.0 means the end of an interval
    # interval_endpoint == 0.0 mean the row is not an interval endpoint
    data.loc[:, 'interval_endpoint'] = data.groupby([data.timestamp.dt.date]).new_interval.diff(periods=-1)

    # Since the difference in the last line was grouped per day, the last
    # row of each day has interval_endpoint==NaT. These rows are the endpoints of the last interval
    # of each day. This means we can set all NaT values to -1.0
    data.loc[data.interval_endpoint.isna(), 'interval_endpoint'] = -1.0

    # There is the special case of intervals of length one, where the start- and end-point are the
    # same row. This happens when there are two consecutive rows with new_interval==1.
    # The column 'single_element_interval' is set to 1.0 if the row is an interval consisting of a
    # single element.
    data.loc[:, 'single_element_interval'] = (data.new_interval.rolling(2).sum() >= 2.0).astype(int).shift(-1)

    # Keep only rows that are interval endpoints.
    data = data[(data.interval_endpoint != 0.0) | (data.single_element_interval != 0.0)]

    # In the data each row of an interval start-point is followed by the corresponding interval
    # end-point. We can thus compute interval the duration off all intervals by subtracting the
    # timestamp of consecutive rows.

    # Note: this also assigns durations to interval endpoints. These durations are the time until
    # the next interval begins.
    data.loc[:, 'duration'] = data.timestamp.diff(periods=-1).abs()

    # We have again to deal with the special case of single point intervals, which have duration
    # min_timedelta.
    data.loc[data.single_element_interval != 0, 'duration'] = min_timedelta

    # Keep only rows that are the start points of an interval.
    data = data[data.new_interval == 1]

    # Rename the timestamp column to begin.
    data = data.rename(columns=dict(timestamp='begin'))
    # Calculate then end time for each interval.
    data.loc[:, 'end'] = data.begin + data.duration

    # Reindex the data, to get a consecutive numbering of each interval.
    data = data.reset_index(drop=True)

    # Delete temporary columns.
    data = data.drop(columns=['delay', 'new_interval', 'interval_endpoint', 'single_element_interval'])

    return data

# ----------------------------------------------------------------------------------------------------------------------
