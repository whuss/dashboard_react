import pandas as pd
from datetime import date, timedelta

from .instruction import get_state_data

from utils.interval import find_intervals
from utils.date import start_of_day, end_of_day

# ----------------------------------------------------------------------------------------------------------------------


def get_scene_durations(device: str, since: date, until: date):
    interval = (start_of_day(since), end_of_day(until))
    state_data = get_state_data(device, interval, resample_rule='1S')

    on_data = state_data[(state_data.power == 'ON') & (state_data.settings == 'OFF')]

    scenes = ['AUTO', 'TASK_HORI', 'TASK_VERT', 'LIGHT_SHOWER']

    scene_data = {scene: find_intervals(on_data[on_data.scene == scene].reset_index()) for scene in scenes}

    # Compute sum of interval durations for each day
    duration_dict = {scene: data.groupby([data.begin.dt.date]).duration.sum() for scene, data in scene_data.items()}
    duration_data = pd.DataFrame(duration_dict).fillna(timedelta(seconds=0))
    return duration_data

# ----------------------------------------------------------------------------------------------------------------------


def get_settings_durations(device: str, since: date, until: date):
    interval = (start_of_day(since), end_of_day(until))
    state_data = get_state_data(device, interval, resample_rule='1S')

    settings_data = state_data[(state_data.power == 'ON') & (state_data.settings == 'ON')]
    settings_intervals = find_intervals(settings_data.reset_index())
    data_dict = dict(duration=settings_intervals.groupby([settings_intervals.begin.dt.date]).duration.sum(),
                     count=settings_intervals.groupby([settings_intervals.begin.dt.date]).duration.count())
    return data_dict

# ----------------------------------------------------------------------------------------------------------------------
