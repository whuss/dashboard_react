from db import PresenceDetectorStatistics

from datetime import date
from utils.date import start_of_day

# ----------------------------------------------------------------------------------------------------------------------


def test_on_off_cycles_empty():
    start_date = start_of_day(date(2020, 3, 1))
    device = "PTL_NONEXISTING"
    data = PresenceDetectorStatistics().on_off_cycle_count(device, start_date)
    assert data.empty

# ----------------------------------------------------------------------------------------------------------------------
