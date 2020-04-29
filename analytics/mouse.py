from db import db, MouseClickPackage, MouseGesturePackage, MouseWheelPackage
import pandas as pd
import numpy as np
from datetime import date
from utils.date import start_of_day, end_of_day

# ----------------------------------------------------------------------------------------------------------------------


def get_mouse_data_raw(device: str, start_date: date, end_date: date) -> pd.DataFrame:
    since = start_of_day(start_date)
    until = end_of_day(end_date)
    mcp = MouseClickPackage
    query = db.session.query(mcp.frame_start,
                             mcp.click_count,
                             mcp.double_click_count) \
        .filter(mcp.device == device) \
        .filter(mcp.frame_start >= since) \
        .filter(mcp.frame_start <= until)

    data_click = pd.DataFrame(query.all())
    if data_click.empty:
        data_click = pd.DataFrame(columns=["frame_start", "click_count", "double_click_count"])

    mwp = MouseWheelPackage
    query = db.session.query(mwp.frame_start,
                             mwp.rotation_distance,
                             mwp.rotation_speed) \
        .filter(mwp.device == device) \
        .filter(mwp.frame_start >= since) \
        .filter(mwp.frame_start <= until)

    data_wheel = pd.DataFrame(query.all())
    if data_wheel.empty:
        data_wheel = pd.DataFrame(columns=["frame_start", "rotation_distance", "rotation_speed"])

    if data_click.empty and data_wheel.empty:
        return pd.DataFrame()

    data_combined = pd.merge(data_click, data_wheel, how='outer', on='frame_start')

    mgp = MouseGesturePackage
    query = db.session.query(mgp.gesture_start.label('frame_start'),
                             mgp.gesture_end,
                             mgp.event_count,
                             mgp.gesture_distance,
                             mgp.gesture_speed,
                             mgp.gesture_deviation) \
        .filter(mgp.device == device) \
        .filter(mgp.gesture_start >= since) \
        .filter(mgp.gesture_start <= until)

    data_gesture = pd.DataFrame(query.all())
    data_gesture['gesture_duration'] = data_gesture.gesture_end - data_gesture.frame_start
    data_gesture['gesture_duration_seconds'] = data_gesture.gesture_duration.dt.total_seconds()
    data_gesture = data_gesture.drop(columns=['gesture_end'])

    data = pd.merge(data_combined, data_gesture, how='outer', on='frame_start')
    if data.empty:
        return data

    data = data.rename(columns=dict(frame_start='timestamp')) \
        .set_index('timestamp') \
        .sort_index()
    return data

# ----------------------------------------------------------------------------------------------------------------------


def get_mouse_data_aggregated(device: str, start_date: date, end_date: date,
                              resample_rule: str = "1Min") -> pd.DataFrame:
    data = get_mouse_data_raw(device, start_date, end_date)
    if data.empty:
        return data

    click_wheel_columns = ['click_count', 'double_click_count', 'rotation_distance']
    data_click_wheel = data.loc[data[click_wheel_columns].fillna(0).sum(axis=1) > 0, click_wheel_columns].fillna(0)

    # the number of basic mouse events in the resampled interval
    click_wheel_event_count = data_click_wheel[['click_count']].resample(resample_rule).count() \
        .rename(columns=dict(click_count='click_wheel_event_count'))

    # the number of mouse gestures in the resampled interval
    gesture_count = data[['event_count']].dropna().resample(resample_rule).count() \
        .rename(columns=dict(event_count='gesture_count'))

    count_data = pd.concat([click_wheel_event_count, gesture_count], axis=1)
    count_data.columns = pd.MultiIndex(levels=[['click_wheel_event_count', 'gesture_count'], ['sum']],
                                       codes=[[0, 1], [0, 0]])

    resampled_data = data.resample(resample_rule).apply([np.sum, np.mean, np.std]).fillna(0)

    merged_data = pd.concat([count_data, resampled_data], axis=1)

    return merged_data

# ----------------------------------------------------------------------------------------------------------------------
