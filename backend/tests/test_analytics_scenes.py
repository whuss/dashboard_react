from analytics.scenes import get_scene_durations, get_settings_durations

from datetime import date
from utils.date import start_of_day, end_of_day
from app import app

# ----------------------------------------------------------------------------------------------------------------------


def test_get_scene_durations():
    device = "PTL_NONEXISTING"
    day = date(2020, 3, 12)
    with app.app_context():
        data = get_scene_durations(device, day)
    assert data.empty

# ----------------------------------------------------------------------------------------------------------------------


def test_get_settings_durations():
    device = "PTL_NONEXISTING"
    day = date(2020, 3, 12)
    with app.app_context():
        data = get_settings_durations(device, day)
    print(data)
    assert data.empty

# ----------------------------------------------------------------------------------------------------------------------
