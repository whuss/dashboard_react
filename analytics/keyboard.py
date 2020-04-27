from db import db, KeyboardPackage
import pandas as pd
from datetime import date
from utils.date import start_of_day, end_of_day

# ----------------------------------------------------------------------------------------------------------------------


def get_keyboard_data(device: str, start_date: date, end_date: date) -> pd.DataFrame:
    since = start_of_day(start_date)
    until = end_of_day(end_date)
    kp = KeyboardPackage
    query = db.session.query(kp.frame_start,
                             kp.key_press_count,
                             kp.delete_press_count,
                             kp.enter_press_count,
                             kp.shift_press_count,
                             kp.space_press_count,
                             kp.press_pause_count,
                             kp.pause_length,
                             kp.keystroke_time,
                             kp.press_to_press_time) \
        .filter(kp.device == device) \
        .filter(kp.frame_start >= since) \
        .filter(kp.frame_start <= until)

    data = pd.DataFrame(query.all())
    if data.empty:
        return data

    data = data.rename(columns=dict(frame_start='timestamp')) \
        .set_index('timestamp')
    return data

# ----------------------------------------------------------------------------------------------------------------------
