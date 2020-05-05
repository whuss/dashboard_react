from analytics.keyboard import get_keyboard_data
from analytics.mouse import get_mouse_data_raw

import pandas as pd
from datetime import date

# ----------------------------------------------------------------------------------------------------------------------


def get_input_data(device: str, start_date: date, end_date: date) -> pd.DataFrame:
    keyboard_data = get_keyboard_data(device, start_date, end_date)
    mouse_data = get_mouse_data_raw(device, start_date, end_date)
    data = pd.merge(keyboard_data, mouse_data, how='outer', left_index=True, right_index=True)
    return data

# ----------------------------------------------------------------------------------------------------------------------
