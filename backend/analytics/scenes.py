import pandas as pd
from datetime import date, timedelta
from typing import Optional

from db import db_cached
from .instruction import get_state_data

from utils.interval import find_intervals
from utils.date import start_of_day, end_of_day

# ----------------------------------------------------------------------------------------------------------------------


@db_cached
def get_scene_durations(device: str, since: date, until: Optional[date] = None) -> pd.DataFrame:
    """Return the total duration of each lighting scene per day.

    @returns: pandas DataFrame with columns 'AUTO', 'TASK_HORI', 'TASK_VERT', 'LIGHT_SHOWER'
    and index column (named: 'date') containing date objects.

    Each column is the total time of the lighting scene (column name) for the day specified
    by the index column. The column entries are timedelta objects.

    The index column is sorted by day.
    """
    if until is None:
        until = date.today()
    interval = (start_of_day(since), end_of_day(until))
    state_data = get_state_data(device, interval, resample_rule='1S')

    on_data = state_data[(state_data.power == 'ON') & (state_data.settings == 'OFF')]

    scenes = ['AUTO', 'TASK_HORI', 'TASK_VERT', 'LIGHT_SHOWER']

    if on_data.empty:
        duration_data = pd.DataFrame(columns=scenes)
    else:
        scene_data = {scene: find_intervals(on_data[on_data.scene == scene].reset_index()) for scene in scenes}

        def compute_total_duration(data_) -> timedelta:
            if data_.empty:
                return timedelta(0)
            return data_.groupby([data_.begin.dt.date]).duration.sum()

        # Compute sum of interval durations for each day
        duration_dict = {scene: compute_total_duration(data) for scene, data in scene_data.items()}
        duration_data = pd.DataFrame(duration_dict).fillna(timedelta(seconds=0))
    duration_data.index.name = 'date'
    return duration_data

# ----------------------------------------------------------------------------------------------------------------------


def get_settings_durations(device: str, since: date, until: Optional[date] = None) -> pd.DataFrame:
    """Returns the total duration of time spend in the ptl windows settings and the number of time
    the settings where opened, per day.

    @returns: pandas DataFrame with columns 'duration' and 'count' and index column named 'date' containing
    date objects.

    'duration': total duration of time spend in ptl windows settings
    'count': number of times the settings where opened.
    """
    if until is None:
        until = date.today()
    interval = (start_of_day(since), end_of_day(until))
    state_data = get_state_data(device, interval, resample_rule='1S')

    settings_data = state_data[(state_data.power == 'ON') & (state_data.settings == 'ON')]

    settings_intervals = find_intervals(settings_data.reset_index())
    if settings_intervals.empty:
        settings_data = pd.DataFrame(columns=['duration', 'count'])
    else:
        data_dict = dict(duration=settings_intervals.groupby([settings_intervals.begin.dt.date]).duration.sum(),
                         count=settings_intervals.groupby([settings_intervals.begin.dt.date]).duration.count())
        settings_data = pd.DataFrame(data_dict).fillna(timedelta(seconds=0))

    settings_data.index.name = 'date'
    return settings_data

# ----------------------------------------------------------------------------------------------------------------------
