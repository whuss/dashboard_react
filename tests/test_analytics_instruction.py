from analytics.instruction import get_state_data, get_instructions_data

from datetime import date
from utils.date import start_of_day, end_of_day
from app import app

# ----------------------------------------------------------------------------------------------------------------------


def test_get_instructions_data_empty():
    device = "PTL_NONEXISTING"
    day = date(2020, 3, 12)
    interval = (start_of_day(day), end_of_day(day))
    with app.app_context():
        data = get_instructions_data(device, interval)
    assert data.empty

# ----------------------------------------------------------------------------------------------------------------------


def test_get_state_data_empty():
    device = "PTL_NONEXISTING"
    day = date(2020, 3, 12)
    interval = (start_of_day(day), end_of_day(day))
    with app.app_context():
        data = get_state_data(device, interval, resample_rule="1s")
    print(data)
    assert data.empty

# ----------------------------------------------------------------------------------------------------------------------
