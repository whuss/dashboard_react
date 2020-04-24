from datetime import datetime, date
from enum import Enum
from typing import Optional

import pandas as pd

from db import TemperaturePackage, PressurePackage, HumidityPackage, BrightnessPackage, GasPackage
from db import db, db_cached_permanent
from utils.interval import TimeInterval, Interval
from utils.date import start_of_day, end_of_day

# ----------------------------------------------------------------------------------------------------------------------


class Sensor(Enum):
    """Encodes all information needed to extract sensor data from the database in a uniform way."""
    TEMPERATURE = 0
    PRESSURE = 1
    HUMIDITY = 2
    GAS = 3
    BRIGHTNESS_LV = 4
    BRIGHTNESS_LH = 5
    BRIGHTNESS_RV = 6
    BRIGHTNESS_RH = 7

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def db_data_column(self) -> str:
        """Name of the DB column containing the sensor data."""
        if self.value <= 2:
            return self.name.lower()
        if self.value == 3:
            return "amount"

        return "brightness"

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def db_source_value(self) -> Optional[str]:
        """If there are multiple sensors providing the some physical unit, this gives the sensor key needed to
        distinguish data from the different sensors.
        """
        if self.value <= 3:
            return None

        sensor_source = self.name.split("_")[1]
        lr = sensor_source[0].lower()
        vh = sensor_source[1].lower()

        return f"brightness_{lr}_{vh}@BH1750"

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def db_package(self) -> db.Model:
        """The database table for this sensor"""
        if self == Sensor.TEMPERATURE:
            return TemperaturePackage
        if self == Sensor.PRESSURE:
            return PressurePackage
        if self == Sensor.HUMIDITY:
            return HumidityPackage
        if self == Sensor.GAS:
            return GasPackage

        return BrightnessPackage

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def data_column(self) -> str:
        """Name of the data column for this sensor in the returned data"""
        return self.name.lower()

# ----------------------------------------------------------------------------------------------------------------------


def _get_sensor_data(device: str, sensor: Sensor, interval: TimeInterval) -> pd.DataFrame:
    """Fetch sensor data from the Database."""
    since, until = interval.begin, interval.end

    dbp = sensor.db_package

    # Find the timestamp of the last sensor value before the selected time interval
    query_last_timestamp = db.session.query(db.func.max(dbp.timestamp).label('timestamp')) \
        .filter(dbp.device == device) \
        .filter(dbp.timestamp < since)

    if sensor.db_source_value:
        query_last_timestamp = query_last_timestamp.filter(dbp.source == sensor.db_source_value)

    sq_last_timestamp = query_last_timestamp.subquery()

    # Get the last recorded sensor value before the selected time interval
    query_last_sensor_value = db.session.query(getattr(dbp, sensor.db_data_column)) \
        .filter(dbp.device == device) \
        .filter(dbp.timestamp == sq_last_timestamp.c.timestamp)

    try:
        first_sensor_value = getattr(query_last_sensor_value.first(), sensor.db_data_column)
    except AttributeError:
        first_sensor_value = None

    # Get sensor values in the selected time interval
    query = db.session.query(getattr(dbp, sensor.db_data_column), dbp.timestamp) \
        .filter(dbp.device == device) \
        .filter(dbp.timestamp >= since) \
        .filter(dbp.timestamp <= until)

    if sensor.db_source_value:
        query = query.filter(dbp.source == sensor.db_source_value)

    query = query.order_by(dbp.timestamp)

    # Create data frame
    data_since = pd.DataFrame({"timestamp": [since], sensor.db_data_column: [first_sensor_value]})
    data_between = pd.DataFrame(query.all())
    if data_between.empty:
        return pd.DataFrame()
    last_sensor_value = data_between[sensor.db_data_column].iloc[-1]
    data_until = pd.DataFrame({"timestamp": [until], sensor.db_data_column: [last_sensor_value]})

    # merge data frames
    data = pd.concat([data_since, data_between, data_until], axis=0) \
        .rename(columns={sensor.db_data_column: sensor.data_column}) \
        .set_index("timestamp") \
        .sort_index() \
        .dropna()

    return data

# ----------------------------------------------------------------------------------------------------------------------


def resample_sensor_data(sensor_data: pd.DataFrame, rule: str = "1Min") -> pd.DataFrame:
    return sensor_data.resample('1S').ffill().resample(rule).mean()

# ----------------------------------------------------------------------------------------------------------------------


def get_sensor_data_single_interval(device: str,
                                    interval: TimeInterval,
                                    rule: str = "1Min",
                                    sensor: Optional[Sensor] = None) -> pd.DataFrame:

    def _get_data(_sensor: Sensor):
        data = _get_sensor_data(device, _sensor, interval)
        if data.empty:
            return data
        return resample_sensor_data(data, rule)

    if sensor:
        return _get_data(sensor)

    return pd.concat([_get_data(sensor) for sensor in Sensor], axis=1)

# ----------------------------------------------------------------------------------------------------------------------


def get_sensor_data_intervals(device: str,
                              intervals: pd.DataFrame,
                              rule: str = "1Min",
                              sensor: Optional[Sensor] = None) -> pd.DataFrame:
    def get_data(_interval):
        return get_sensor_data_single_interval(device, _interval, rule=rule, sensor=sensor)

    data = []
    for interval in intervals.itertuples():
        print(f"Get data for interval: {interval.begin} - {interval.end}")
        data.append(get_data(interval))

    return pd.concat(data, axis=0)

# ----------------------------------------------------------------------------------------------------------------------


def get_sensor_data(device, intervals, rule: str = "1Min", sensor: Optional[Sensor] = None) -> pd.DataFrame:
    if isinstance(intervals, pd.DataFrame):
        return get_sensor_data_intervals(device, intervals, rule, sensor)

    # intervals is actually a single interval
    interval = intervals

    if isinstance(interval, Interval):
        return get_sensor_data_single_interval(device, interval, rule, sensor)

    if isinstance(interval, tuple):
        if len(interval) == 2 and isinstance(interval[0], datetime) and isinstance(interval[1], datetime):
            begin, end = interval
            return get_sensor_data_single_interval(device, TimeInterval(begin, end), rule, sensor)

    raise TypeError(f"Incorrect type for parameter intervals: {intervals}.")

# ----------------------------------------------------------------------------------------------------------------------


@db_cached_permanent
def get_sensor_data_for_day(device: str, day: date, rule: str = "1s") -> pd.DataFrame:
    interval = (start_of_day(day), end_of_day(day))
    return get_sensor_data(device, interval, rule=rule)

# ----------------------------------------------------------------------------------------------------------------------
