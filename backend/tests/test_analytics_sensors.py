from analytics.sensors import get_sensor_data_for_day

from datetime import date
from app import app

# ----------------------------------------------------------------------------------------------------------------------


def test_get_sensor_data_for_day():
    device = "PTL_NONEXISTING"
    day = date(2020, 3, 12)
    with app.app_context():
        data = get_sensor_data_for_day(device, day)
    assert data.empty

# ----------------------------------------------------------------------------------------------------------------------
