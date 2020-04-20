import functools
import inspect

from datetime import datetime, timedelta, date, time
from typing import Optional

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import mysql
from utils.date import format_timespan_sloppy

# ----------------------------------------------------------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------------------------------------------------------


db = SQLAlchemy()

# ----------------------------------------------------------------------------------------------------------------------
# Custom column types
# ----------------------------------------------------------------------------------------------------------------------


class PickleTypeMedium(db.PickleType):
    impl = mysql.MEDIUMBLOB

# ----------------------------------------------------------------------------------------------------------------------
# Define DB Model
# ----------------------------------------------------------------------------------------------------------------------


class CachePackage(db.Model):
    __bind_key__ = "cache"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    query = db.Column(db.String(100), index=True, nullable=False)
    sha256 = db.Column(db.String(64), index=True, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    data = db.Column(PickleTypeMedium, nullable=False)

# ----------------------------------------------------------------------------------------------------------------------

class DataFramePackage(db.Model):
    __bind_key__ = "cache"
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(20))
    date = db.Column(db.Date)
    query = db.Column(db.String(100))
    data = db.Column(PickleTypeMedium)

# ----------------------------------------------------------------------------------------------------------------------


class DeviceDataFramePackage(db.Model):
    __bind_key__ = "cache"
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(20))
    query = db.Column(db.String(100))
    data = db.Column(PickleTypeMedium)

# ----------------------------------------------------------------------------------------------------------------------


class DeadManPackage(db.Model):
    __tablename__ = 'DeadManPackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_db_dead_man_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    service = db.Column('service_sn', key='service')
    source = db.Column('ix_source_sn', key='source')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    create_dtm = db.Column('create_dtm')


# ----------------------------------------------------------------------------------------------------------------------


class DbSizePackage(db.Model):
    __tablename__ = 'DbSizePackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_db_size_package_id', db.Integer, key='id', primary_key=True)
    date = db.Column('ix_data_dtm', key='date')
    data_size_in_mb = db.Column('data_size_in_mb', key='data_size_in_mb')
    index_size_in_mb = db.Column('index_size_in_mb', key='index_size_in_mb')

# ----------------------------------------------------------------------------------------------------------------------


class ErrorPackage(db.Model):
    __tablename__ = 'ErrorPackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_error_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    service = db.Column('service_sn', key='service')
    source = db.Column('ix_source_sn', key='source')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    errno = db.Column('number_int', key="errno")
    message = db.Column('message_str', key="message")
    create_dtm = db.Column('create_dtm')


# ----------------------------------------------------------------------------------------------------------------------


class LoggerPackage(db.Model):
    __tablename__ = 'LoggerPackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_logger_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    service = db.Column('service_sn', key='service')
    source = db.Column('ix_source_sn', key='source')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    filename = db.Column('filename_str', key='filename')
    line_number = db.Column('line_number_int', key='line_number')
    log_level = db.Column('log_level_ind', key='log_level')
    message = db.Column('message_str', key="message")
    create_dtm = db.Column('create_dtm')


# ----------------------------------------------------------------------------------------------------------------------


class VersionPackage(db.Model):
    __tablename__ = 'VersionPackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_version_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    service = db.Column('service_sn', key='service')
    source = db.Column('ix_source_sn', key='source')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    ip = db.Column('ip_sn', key='ip')
    commit = db.Column('commit_sn', key="commit")
    branch = db.Column('branch_sn', key="branch")
    version_timestamp = db.Column('version_timestamp_dtm', key='version_timestamp')
    create_dtm = db.Column('create_dtm')


# ----------------------------------------------------------------------------------------------------------------------


class DeviceInfo(db.Model):
    __tablename__ = 'DeviceInfo'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_device_info_id', db.Integer, key='id', primary_key=True)
    device = db.Column('uk_device_sn', key='device')
    mode = db.Column('device_mode_ind', key='mode')
    last_update = db.Column('last_update_dtm', key='last_update')
    create_dtm = db.Column('create_dtm')


# ----------------------------------------------------------------------------------------------------------------------


class InstructionPackage(db.Model):
    __tablename__ = 'InstructionPackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_instruction_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    service = db.Column('service_sn', key='service')
    source = db.Column('ix_source_sn', key='source')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    instruction = db.Column('instruction_ind', key='instruction')
    target = db.Column('target_ind', key='target')
    value = db.Column('value_jsn', key='value')
    create_dtm = db.Column('create_dtm')

    # ------------------------------------------------------------------------------------------------------------------

    # FIXME: make static, get mapped column names
    def get_columns(self):
        return self.__table__.columns

    # ------------------------------------------------------------------------------------------------------------------

    def get_column_names(self):
        return self.get_columns().keys()


# ----------------------------------------------------------------------------------------------------------------------


class LightingPackage(db.Model):
    __tablename__ = 'LightingPackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_lighting_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    mode = db.Column('ix_mode_ind', key='mode')
    create_dtm = db.Column('create_dtm')


# ----------------------------------------------------------------------------------------------------------------------


class MouseGesturePackage(db.Model):
    __tablename__ = 'MouseGesturePackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_mouse_gesture_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    gesture_start = db.Column('gesture_start_dtm', key='gesture_start')
    gesture_end = db.Column('gesture_end_dtm', key='gesture_end')
    event_count = db.Column('event_count_int', key='event_count')
    gesture_distance = db.Column('gesture_distance_dbl', key='gesture_distance')
    gesture_speed = db.Column('gesture_speed_dbl', key='gesture_speed')
    gesture_deviation = db.Column('gesture_deviation_dbl', key='gesture_deviation')
    create_dtm = db.Column('create_dtm')


# ----------------------------------------------------------------------------------------------------------------------


class TemperaturePackage(db.Model):
    __tablename__ = 'TemperaturePackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_temperature_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    temperature = db.Column('temperature_dbl', key='temperature')
    unit = db.Column('unit_sn', key='unit')
    create_dtm = db.Column('create_dtm')


# ----------------------------------------------------------------------------------------------------------------------


class HumidityPackage(db.Model):
    __tablename__ = 'HumidityPackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_humidity_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    humidity = db.Column('humidity_dbl', key='humidity')
    unit = db.Column('unit_sn', key='unit')
    create_dtm = db.Column('create_dtm')


# ----------------------------------------------------------------------------------------------------------------------


class PressurePackage(db.Model):
    __tablename__ = 'PressurePackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_pressure_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    pressure = db.Column('pressure_dbl', key='pressure')
    unit = db.Column('unit_sn', key='unit')
    create_dtm = db.Column('create_dtm')


# ----------------------------------------------------------------------------------------------------------------------


class GasPackage(db.Model):
    __tablename__ = 'GasPackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_gas_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    gas = db.Column('gas_ind', key='gas')
    amount = db.Column('amount_dbl', key='amount')
    unit = db.Column('unit_sn', key='unit')
    create_dtm = db.Column('create_dtm')


# ----------------------------------------------------------------------------------------------------------------------


class BrightnessPackage(db.Model):
    __tablename__ = 'BrightnessPackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_brightness_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    brightness = db.Column('brightness_int', key='brightness')
    source = db.Column('ix_source_sn', key='source')
    unit = db.Column('unit_sn', key='unit')
    create_dtm = db.Column('create_dtm')


# ----------------------------------------------------------------------------------------------------------------------


class LoudnessPackage(db.Model):
    __tablename__ = 'LoudnessPackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_loudness_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    loudness = db.Column('loudness_dbl', key='loudness')
    unit = db.Column('unit_sn', key='unit')
    create_dtm = db.Column('create_dtm')

# ----------------------------------------------------------------------------------------------------------------------
# DB Cache
# ----------------------------------------------------------------------------------------------------------------------


def _hash_id(value):
    from hashlib import sha256
    return sha256(repr(value).encode()).hexdigest()

# ----------------------------------------------------------------------------------------------------------------------


def find_in_cache(query_name: str, parameter_digest: str) -> Optional[CachePackage]:
    cp = CachePackage
    query = db.session.query(cp) \
        .filter(cp.query == query_name) \
        .filter(cp.sha256 == parameter_digest)

    return query.first()


# ----------------------------------------------------------------------------------------------------------------------


def db_cached(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        # Collect function arguments by chaining together positional,
        # defaulted, extra positional and keyword arguments.
        f_name = f"{fn.__module__}.{fn.__name__}"
        # signature = inspect.signature(fn)
        parameter_repr = f"args: {args} kwargs: {kwargs}"
        parameter_digest = _hash_id(parameter_repr)

        print(f"db_cached: name={f_name}, parameter_digest={parameter_digest}")
        cached_data = find_in_cache(f_name, parameter_digest)

        if cached_data:
            print(f"db_cached: found cached value.")
            expiration_time = timedelta(days=1)
            if datetime.now() - cached_data.timestamp < expiration_time:
                # no update needed
                print(f"db_cached: no update needed: return cached data.")
                return cached_data.data
            print(f"db_cached: cached value expired.")
        else:
            print(f"db_cached: no cached value found.")

        # Calculate data
        print(f"db_cached: Calculate data.")
        data = fn(*args, **kwargs)

        if cached_data:
            print(f"db_cached: update cached data.")
            # update cached_data
            CachePackage.update() \
                .where(CachePackage.id == cached_data.id) \
                .values(timestamp=datetime.now(),
                        data=data)
            db.session.commit()
        else:
            # insert data into cache
            print(f"db_cached: insert data into cache.")
            data_package = CachePackage(query=f_name,
                                        sha256=parameter_digest,
                                        timestamp=datetime.now(),
                                        data=data)
            db.session.add(data_package)
            db.session.commit()

        print(f"db_cached: return data.")
        return data

    return wrapped

# ----------------------------------------------------------------------------------------------------------------------
# DB Queries
# ----------------------------------------------------------------------------------------------------------------------


class Dashboard(object):
    def __init__(self):
        # ---- Device query ----
        self.query_device = db.session.query(DeviceInfo.device)

        # ---- Info query ----
        self.query_info = db.session.query(DeviceInfo.device,
                                           DeviceInfo.mode)

        # ---- Mode query ----
        lp = LightingPackage
        lastone = db.func.max(lp.id).label('lastone')
        last_light_package = db.session.query(lp.device, lastone) \
            .group_by(lp.device)

        sq = last_light_package.subquery()
        # last know operating mode per PTL-device
        self.query_mode = db.session.query(lp.device, lp.timestamp, lp.mode) \
            .join(sq, sq.columns.lastone == lp.id)
        super().__init__()

    # ------------------------------------------------------------------------------------------------------------------

    def devices(self):
        devices = self.query_device.all()
        return [device[0] for device in devices]

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def info(device: str):
        print(f"Dashboard.device_info(device={device})")
        query_study_mode = db.session.query(DeviceInfo.mode.label('study_mode')) \
            .filter(DeviceInfo.device == device)

        data = query_study_mode.first()
        print(f"data={data}")
        if data:
            study_mode = data.study_mode
        else:
            study_mode = ""

        print(f"study_mode={study_mode}")

        dmp = DeadManPackage
        query_connection = db.session.query(db.func.max(dmp.timestamp).label('last_connection')) \
            .filter(dmp.device == device) \

        data = query_connection.first()[0]
        print(f"query_connection data = {data}")
        if data:
            last_connection = data
            offline_duration = datetime.now() - last_connection
        else:
            last_connection = None
            offline_duration = None

        def _health_status(_offline_duration):
            if _offline_duration and _offline_duration < timedelta(minutes=2):
                return "HEALTHY"
            else:
                return "SICK"

        health_status = _health_status(offline_duration)

        def _sick_reason(_health_status, _last_connection, _offline_duration):
            if not _last_connection:
                return "Never online"

            if _health_status == "SICK":
                return f"Offline for {_offline_duration}"
            else:
                return ""

        sick_reason = _sick_reason(health_status, last_connection, offline_duration)

        print(f"db: sick_reason={sick_reason}, last_connection={last_connection}")

        return dict(device=device,
                    study_mode=study_mode,
                    last_connection=last_connection,
                    offline_duration=format_timespan_sloppy(offline_duration) if offline_duration else "",
                    health_status=health_status,
                    sick_reason=sick_reason)

# ----------------------------------------------------------------------------------------------------------------------


class SensorData(object):
    def __init__(self):
        # ---- Device query ----
        self.query_device = db.session.query(DeviceInfo.device)

        tp = TemperaturePackage
        self.sq_temperature = db.session.query(tp.device, db.func.max(tp.timestamp), tp.temperature, tp.unit) \
            .group_by(tp.device) \
            .subquery()

        hp = HumidityPackage
        self.sq_humidity = db.session.query(hp.device, db.func.max(hp.timestamp), hp.humidity, hp.unit) \
            .group_by(hp.device) \
            .subquery()

        pp = PressurePackage
        self.sq_pressure = db.session.query(pp.device, db.func.max(pp.timestamp), pp.pressure, pp.unit) \
            .group_by(pp.device) \
            .subquery()

        gp = GasPackage
        self.sq_gas = db.session.query(gp.device, db.func.max(gp.timestamp), gp.gas, gp.amount, gp.unit) \
            .group_by(gp.device) \
            .subquery()

        bp = BrightnessPackage
        self.sq_brightness = db.session.query(bp.device, db.func.max(bp.timestamp), bp.brightness, bp.unit) \
            .filter(bp.source == "brightness_l_h@BH1750") \
            .group_by(bp.device) \
            .subquery()

        lp = LoudnessPackage
        self.sq_loudness = db.session.query(lp.device, db.func.max(lp.timestamp), lp.loudness, lp.unit) \
            .group_by(lp.device) \
            .subquery()

        super().__init__()

    # ------------------------------------------------------------------------------------------------------------------

    def current_sensor_data(self):
        sq_temperature = self.sq_temperature
        sq_humidity = self.sq_humidity
        sq_pressure = self.sq_pressure
        sq_gas = self.sq_gas
        sq_brightness = self.sq_brightness
        sq_loudness = self.sq_loudness

        return self.query_device \
            .outerjoin(sq_temperature, DeviceInfo.device == sq_temperature.c.device) \
            .add_columns(sq_temperature.c.temperature, sq_temperature.c.unit.label('temperature_unit')) \
            .outerjoin(sq_humidity, DeviceInfo.device == sq_humidity.c.device) \
            .add_columns(sq_humidity.c.humidity, sq_humidity.c.unit.label('humidity_unit')) \
            .outerjoin(sq_pressure, DeviceInfo.device == sq_pressure.c.device) \
            .add_columns(sq_pressure.c.pressure, sq_pressure.c.unit.label('pressure_unit')) \
            .outerjoin(sq_gas, DeviceInfo.device == sq_gas.c.device) \
            .add_columns(sq_gas.c.gas, sq_gas.c.amount.label('gas_amount'), sq_gas.c.unit.label('gas_unit')) \
            .outerjoin(sq_brightness, DeviceInfo.device == sq_brightness.c.device) \
            .add_columns(sq_brightness.c.brightness, sq_brightness.c.unit.label('brightness_unit')) \
            .outerjoin(sq_loudness, DeviceInfo.device == sq_loudness.c.device) \
            .add_columns(sq_loudness.c.loudness, sq_loudness.c.unit.label('loudness_unit')) \
            .order_by(DeviceInfo.device) \
            .all()

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def temperature(since, until, device=None):
        tp = TemperaturePackage
        query = db.session.query(tp.device, tp.temperature, tp.unit, tp.timestamp) \
            .filter(tp.timestamp >= since) \
            .filter(tp.timestamp <= until)

        if device:
            query = query.filter(tp.device == device)

        query = query.order_by(tp.device, tp.timestamp)
        data = query.all()

        return _timeseries(data, 'temperature')

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def brightness(since, until, device=None):
        """ Return timeseries of Brightness package for all devices

        Note:
        -----
        The PTL has 4 different brightness sensors. Which can be distinguied by column BrightnessBackage.source
        """
        bp = BrightnessPackage
        query = db.session.query(bp.device, bp.brightness, bp.unit, bp.timestamp, bp.source) \
            .filter(bp.timestamp >= since) \
            .filter(bp.timestamp <= until)

        if device:
            query = query.filter(bp.device == device)

        query = query.order_by(bp.device, bp.timestamp)

        data = pd.DataFrame(query.all())
        data = data.set_index(['device', 'source', data.index])
        return data

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def humidity(since, until, device=None):
        hp = HumidityPackage
        query = db.session.query(hp.device, hp.humidity, hp.unit, hp.timestamp) \
            .filter(hp.timestamp >= since) \
            .filter(hp.timestamp <= until)

        if device:
            query = query.filter(hp.device == device)

        query = query.order_by(hp.device, hp.timestamp)
        data = query.all()

        return _timeseries(data, 'humidity')

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def pressure(since, until, device=None):
        pp = PressurePackage
        query = db.session.query(pp.device, pp.pressure, pp.unit, pp.timestamp) \
            .filter(pp.timestamp >= since) \
            .filter(pp.timestamp <= until)

        if device:
            query = query.filter(pp.device == device)

        query = query.order_by(pp.device, pp.timestamp)
        data = query.all()

        return _timeseries(data, 'pressure')

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gas(since, until, device=None):
        gp = GasPackage
        query = db.session.query(gp.device, gp.gas, gp.amount, gp.unit, gp.timestamp) \
            .filter(gp.timestamp >= since) \
            .filter(gp.timestamp <= until)

        if device:
            query = query.filter(gp.device == device)

        query = query.order_by(gp.device, gp.timestamp)
        data = query.all()

        return _timeseries(data, 'amount')


# ----------------------------------------------------------------------------------------------------------------------


class PresenceDetectorStatistics(object):
    def __init__(self):
        self.query_device = db.session.query(DeviceInfo.device)

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _on_off(x):
        return 1 if x == "ON" else 0

    # ------------------------------------------------------------------------------------------------------------------

    def debug_on_off_timeseries(self, since, until):
        ip = InstructionPackage
        sq_on_off = db.session.query(ip.device, ip.service, ip.source, ip.timestamp, ip.instruction, ip.target,
                                     ip.value) \
            .filter(ip.source.contains("Lullaby")) \
            .filter(ip.instruction == "MODE") \
            .filter(ip.target == "POWER") \
            .filter(ip.timestamp >= since) \
            .filter(ip.timestamp <= until) \
            .subquery()

        query = self.query_device \
            .outerjoin(sq_on_off, DeviceInfo.device == sq_on_off.c.device) \
            .add_columns(sq_on_off.c.timestamp, sq_on_off.c.value)

        data = pd.DataFrame(query.all())
        data.value = data.value.apply(PresenceDetectorStatistics._on_off)
        data = data.set_index(['device', data.index])

        return data

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def on_off_timeseries(since, until, device=None):
        ip = InstructionPackage
        query = db.session.query(ip.device, ip.timestamp, ip.value) \
            .filter(ip.source.contains("Lullaby")) \
            .filter(ip.instruction == "MODE") \
            .filter(ip.target == "POWER") \
            .filter(ip.timestamp >= since) \
            .filter(ip.timestamp <= until) \
            .filter(ip.device != "PTL_DEFAULT")

        sq_index_since = db.session.query(ip.device, db.func.max(ip.timestamp).label('timestamp_since')) \
            .filter(ip.source.contains("Lullaby")) \
            .filter(ip.instruction == "MODE") \
            .filter(ip.target == "POWER") \
            .filter(ip.timestamp < since) \
            .filter(ip.device != "PTL_DEFAULT") \
            .group_by(ip.device) \
            .subquery()

        query_since = db.session.query(ip.device, ip.timestamp, ip.value) \
            .filter(ip.source.contains("Lullaby")) \
            .filter(ip.instruction == "MODE") \
            .filter(ip.target == "POWER") \
            .filter(ip.timestamp < since) \
            .filter(ip.device != "PTL_DEFAULT") \
            .join(sq_index_since, sq_index_since.c.device == ip.device) \
            .filter(ip.timestamp == sq_index_since.c.timestamp_since)

        if device:
            query = query.filter(ip.device == device)
            query_since = query_since.filter(ip.device == device)

        data = pd.DataFrame(query.all())
        data_since = pd.DataFrame(query_since.all())
        data_since.timestamp = since

        data = pd.concat([data_since, data], ignore_index=True)

        if data.empty:
            return data

        data.value = data.value.apply(PresenceDetectorStatistics._on_off)

        data = data.sort_values(['device', 'timestamp'])

        # remove consecutive rows with the same 'value'
        data['keep_row'] = data.groupby('device').value.diff(periods=1)
        data = data[data.keep_row != 0.0]
        # merge intervals, such that each row in the data corresponds to one
        # interval ['begin', 'end'] where the light has been either on ('value'=1)
        # or off ('value' = 0) the whole time.
        data = data.rename(columns=dict(timestamp='begin'))
        data['duration'] = data.groupby('device').begin.diff(periods=-1).abs()
        data['end'] = data.begin + data.duration

        # set the end of the last interval to the end of the time interval [since, until]
        data.end = data.end.fillna(until)
        # fill NaT values for column duration
        data.duration = data.end - data.begin

        data = data.set_index(['device', data.index])
        return data[['begin', 'value', 'duration', 'end']]

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @db_cached
    def on_off_cycle_count(device: str, since: date):
        ip = InstructionPackage

        query = db.session.query(ip.device, ip.timestamp, ip.instruction, ip.value) \
            .filter(ip.device == device) \
            .filter(ip.timestamp >= since) \
            .filter(ip.source.contains("Lullaby")) \
            .filter(ip.instruction == "MODE") \
            .filter(ip.target == "POWER") \
            .filter(ip.value == "ON") \


        def is_night(timestamp):
            time = timestamp.time()
            return time.hour <= 6 or time.hour >= 22

        data: pd.DataFrame = pd.DataFrame(query.all())
        data['date'] = data.timestamp.apply(lambda x: x.date())
        data['night'] = data.timestamp.apply(is_night)
        data = data.set_index(['date', 'night', data.index])
        data = data.groupby(['date', 'night']).count()
        data = data.drop(columns=['timestamp'])
        data = data.rename(columns=dict(value="count"))
        return data

# ----------------------------------------------------------------------------------------------------------------------


class Errors(object):
    @staticmethod
    def crashes(device=None):
        lp = LoggerPackage
        query = db.session.query(lp.device, lp.source, lp.timestamp, lp.filename, lp.line_number, lp.log_level,
                                 lp.message) \
            .filter(lp.log_level == "CRITICAL")

        if device:
            query = query.filter(lp.device == device)

        query = query.filter(lp.device != "PTL_DEFAULT")

        data = pd.DataFrame(query.all())

        data = data.set_index(['device', data.index])
        return data

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def crash_histogram(device: str, since: datetime):
        from sqlalchemy import Date
        lp = LoggerPackage
        query = db.session \
            .query(lp.device,
                   lp.timestamp.cast(Date).label('date'),
                   db.func.count(lp.timestamp).label('crash_count')) \
            .filter(lp.log_level.in_(["CRITICAL"])) \
            .filter(lp.device != "PTL_DEFAULT") \
            .group_by('date') \
            .group_by(lp.device)

        data = pd.DataFrame(query.all())
        data = data.set_index(['device'])

        if device not in data.index:
            return pd.DataFrame(columns=['date', 'crash_count'])

        data = data.loc[device]
        return data[data.date >= since.date()].reset_index(drop=True)

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def restart_histogram(device: str, since: datetime):
        from sqlalchemy import Date
        vp = VersionPackage
        query = db.session \
            .query(vp.timestamp.cast(Date).label('date'),
                   db.func.count(vp.timestamp).label('restart_count')) \
            .filter(vp.timestamp >= since) \
            .filter(vp.device == device) \
            .group_by('date')

        data = pd.DataFrame(query.all())
        return data

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @db_cached
    def crash_restart_histogram(device: str, since: datetime):
        crash_histogram = Errors.crash_histogram(device, since)
        restart_histogram = Errors.restart_histogram(device, since)

        if crash_histogram.empty and restart_histogram.empty:
            return pd.DataFrame()

        if crash_histogram.empty:
            combined_histogram = restart_histogram
        elif restart_histogram.empty:
            combined_histogram = crash_histogram
        else:
            combined_histogram = crash_histogram.merge(restart_histogram, on='date', how='outer').fillna(value=0)

        # compute string of the end of the day for url creation
        def end_of_day(row):
            return (row.date + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

        combined_histogram['end_of_day'] = combined_histogram.apply(end_of_day, axis=1)
        return combined_histogram.set_index(['date'])

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def errors(device=None):
        lp = LoggerPackage
        query = db.session.query(lp.device, lp.source, lp.timestamp, lp.filename,
                                 lp.line_number, lp.log_level, lp.message) \
            .filter(lp.log_level == "ERROR")

        if device:
            query = query.filter(lp.device == device)

        query = query.filter(lp.device != "PTL_DEFAULT")

        data = pd.DataFrame(query.all())

        data = data.set_index(['device'])
        return data

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def error_histogram():
        from sqlalchemy import Date
        lp = LoggerPackage
        query = db.session \
            .query(lp.device,
                   lp.timestamp.cast(Date).label('date'),
                   db.func.count(lp.timestamp).label('error_count')) \
            .filter(lp.log_level.in_(["ERROR", "CRITICAL"])) \
            .filter(lp.device != "PTL_DEFAULT") \
            .group_by('date') \
            .group_by(lp.device)

        data = pd.DataFrame(query.all())
        data['end_of_day'] = data.date.apply(lambda x: x + timedelta(days=1))
        data = data.set_index(['device', 'date'])
        return data

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def error_heatmap():
        from sqlalchemy import Date
        lp = LoggerPackage
        query = db.session \
            .query(lp.device,
                   lp.filename,
                   lp.line_number,
                   lp.timestamp.cast(Date).label('date'),
                   db.func.count(lp.timestamp).label('error_count')) \
            .filter(lp.log_level.in_(["ERROR", "CRITICAL"])) \
            .filter(lp.device != "PTL_DEFAULT") \
            .group_by('date') \
            .group_by(lp.filename) \
            .group_by(lp.line_number) \
            .group_by(lp.device)

        data = pd.DataFrame(query.all())
        data['end_of_day'] = data.date.apply(lambda x: x + timedelta(days=1))
        data = data.set_index(['device', 'date'])
        return data

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def crash_at_time(device, time):
        lp = LoggerPackage
        query = db.session.query(lp.device, lp.id, lp.log_level, lp.timestamp) \
            .filter(lp.log_level == "CRITICAL") \
            .filter(lp.device == device) \
            .filter(lp.timestamp <= time) \
            .filter(lp.timestamp >= time - timedelta(minutes=5))

        data = pd.DataFrame(query.all())

        # A crash happened if the query returned something
        return not data.empty

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def logs(device_id=None, since=None, until=None, num_lines=None, log_level="TRACE", page=None,
             filename=None, line_number=None):

        print(f"device_id={device_id}")
        print(f"since={since}")
        print(f"until={until}")
        print(f"num_lines={num_lines}")
        print(f"log_level={log_level}")
        print(f"page={page}")
        print(f"filename={filename}")
        print(f"line_number={line_number}")
        MAX_LOG_ITEMS_PER_PAGE = 50
        lp = LoggerPackage

        sq_device = db.session.query(DeviceInfo.device).subquery()

        query = db.session.query(lp.device, lp.source, lp.timestamp, lp.filename, lp.line_number, lp.log_level,
                                 lp.message) \
            .outerjoin(sq_device, sq_device.c.device == lp.device) \
            .order_by(lp.device)

        query = query.filter(lp.device != "PTL_DEFAULT")

        if since:
            query = query.filter(lp.timestamp >= since)

        if until:
            query = query.filter(lp.timestamp <= until)

        if device_id:
            query = query.filter(lp.device == device_id)

        if log_level != "TRACE":
            if log_level == "DEBUG":
                _filter = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
            elif log_level == "INFO":
                _filter = ["CRITICAL", "ERROR", "WARNING", "INFO"]
            elif log_level == "WARNING":
                _filter = ["CRITICAL", "ERROR", "WARNING"]
            elif log_level == "ERROR":
                _filter = ["CRITICAL", "ERROR"]
            elif log_level == "CRITICAL":
                _filter = ["CRITICAL"]
            else:
                _filter = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE"]

            query = query.filter(lp.log_level.in_(_filter))

        if filename:
            query = query.filter(lp.filename == filename)

        if line_number:
            query = query.filter(lp.line_number == line_number)

        if num_lines:
            query = query.order_by(lp.timestamp.desc()) \
                .slice(1, num_lines)

        if page is not None:
            print(f"Pageinate: page={page}")
            pagination = query.paginate(page, MAX_LOG_ITEMS_PER_PAGE, False)
            data = pagination.items
        else:
            data = query.all()
            pagination = None

        data = pd.DataFrame(data)

        if num_lines:
            data = data.sort_values(by=['timestamp'])

        if not data.empty:
            data = data.set_index(['device', data.index])
        return data, pagination

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def version(device_id=None, check_crashes=True):
        vp = VersionPackage

        sq_device = db.session.query(DeviceInfo.device).subquery()

        query = db.session.query(vp.device, vp.timestamp, vp.version_timestamp, vp.branch, vp.commit, vp.ip) \
            .filter(vp.timestamp >= datetime.now() - timedelta(days=2)) \
            .outerjoin(sq_device, sq_device.c.device == vp.device) \
            .order_by(vp.device)

        query = query.filter(vp.device != "PTL_DEFAULT")

        if device_id:
            query = query.filter(vp.device == device_id)

        data = pd.DataFrame(query.all())

        if check_crashes:
            data['crash'] = data.apply(lambda row: Errors.crash_at_time(row['device'], row['timestamp']), axis=1)

        data = data.set_index(['device', data.index])
        return data


# ----------------------------------------------------------------------------------------------------------------------


class ModeStatistics(object):
    @dataclass(order=True)
    class ModeCounts:
        device: str = field(compare=True)
        auto: int = 0
        off: int = 0
        manual: int = 0
        light_shower: int = 0

        def data(self):
            return [self.auto, self.off, self.manual, self.light_shower]

    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        query_device = db.session.query(DeviceInfo.device)

        lp = LightingPackage
        sq_mode = db.session.query(lp.device, lp.mode, db.func.count(lp.mode).label('count')) \
            .group_by(lp.mode) \
            .group_by(lp.device) \
            .order_by(lp.device) \
            .subquery()

        self.query_mode = query_device.outerjoin(sq_mode, DeviceInfo.device == sq_mode.c.device) \
            .add_columns(sq_mode.c.mode, sq_mode.c.count) \
            .order_by(DeviceInfo.device)

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _table_to_python(table):
        data = {}
        for row in table:
            if row.device not in data:
                data[row.device] = ModeStatistics.ModeCounts(device=row.device)
            if row.mode:
                setattr(data[row.device], row.mode.lower(), row.count)
        return sorted(data.values())

    # ------------------------------------------------------------------------------------------------------------------

    def mode_counts(self):
        return ModeStatistics._table_to_python(self.query_mode.all())


# ----------------------------------------------------------------------------------------------------------------------


class MouseData(object):
    def __init__(self):
        # ---- Device query ----
        self.query_device = db.session.query(DeviceInfo.device)

    # ------------------------------------------------------------------------------------------------------------------

    def gesture_data(self, since, until):
        column_names = dict(gesture_distance="distance",
                            gesture_speed="speed",
                            gesture_deviation="deviation")

        mgp = MouseGesturePackage
        sq_mouse = db.session.query(mgp.device, mgp.timestamp, mgp.gesture_start, mgp.gesture_end,
                                    mgp.gesture_distance, mgp.gesture_speed, mgp.gesture_deviation) \
            .filter(mgp.timestamp >= since) \
            .filter(mgp.timestamp <= until) \
            .subquery()

        query = self.query_device \
            .outerjoin(sq_mouse, sq_mouse.c.device == DeviceInfo.device) \
            .add_columns(sq_mouse.c.timestamp, sq_mouse.c.gesture_start, sq_mouse.c.gesture_end,
                         sq_mouse.c.gesture_distance, sq_mouse.c.gesture_speed, sq_mouse.c.gesture_deviation) \
            .order_by(sq_mouse.c.device, sq_mouse.c.timestamp)

        data = pd.DataFrame(query.all())
        data = data.set_index(['device', data.index])

        devices = data.index.levels[0]
        data_dict = {}
        for device in devices:
            df = data.loc[device]
            df = df.sort_values(by=['timestamp'])
            df = df.rename(columns=column_names)
            data_dict[device] = df.dropna()

        return data_dict


# ----------------------------------------------------------------------------------------------------------------------


class DatabaseDelay(object):
    def __init__(self):
        # ---- Device query ----
        self.query_device = db.session.query(DeviceInfo.device)

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def size():
        dp = DbSizePackage
        query = db.session.query(dp.date, dp.data_size_in_mb, dp.index_size_in_mb)
        data = pd.DataFrame(query.all())

        data['total_size'] = data.data_size_in_mb + data.index_size_in_mb

        return data

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def package_delay(start_date, end_date):
        p = InstructionPackage
        query1 = db.session.query(p.device, p.create_dtm, p.timestamp) \
            .filter(p.timestamp >= start_date) \
            .filter(p.timestamp <= end_date)
        # p = LightingPackage
        # query2 = db.session.query(p.device, p.create_dtm, p.timestamp) \
        #                 .filter(p.timestamp >= start_date) \
        #                 .filter(p.timestamp <= end_date)
        # p = MouseGesturePackage
        # query3 = db.session.query(p.device, p.create_dtm, p.timestamp) \
        #                 .filter(p.timestamp >= start_date) \
        #                 .filter(p.timestamp <= end_date)
        p = TemperaturePackage
        query4 = db.session.query(p.device, p.create_dtm, p.timestamp) \
            .filter(p.timestamp >= start_date) \
            .filter(p.timestamp <= end_date)
        # p = HumidityPackage
        # query5 = db.session.query(p.device, p.create_dtm, p.timestamp) \
        #                 .filter(p.timestamp >= start_date) \
        #                 .filter(p.timestamp <= end_date)
        # p = PressurePackage
        # query6 = db.session.query(p.device, p.create_dtm, p.timestamp) \
        #                 .filter(p.timestamp >= start_date) \
        #                 .filter(p.timestamp <= end_date)
        # p = GasPackage
        # query7 = db.session.query(p.device, p.create_dtm, p.timestamp) \
        #                 .filter(p.timestamp >= start_date) \
        #                 .filter(p.timestamp <= end_date)
        # p = BrightnessPackage
        # query8 = db.session.query(p.device, p.create_dtm, p.timestamp) \
        #                 .filter(p.timestamp >= start_date) \
        #                 .filter(p.timestamp <= end_date)
        # p = LoudnessPackage
        # query9 = db.session.query(p.device, p.create_dtm, p.timestamp) \
        #                 .filter(p.timestamp >= start_date) \
        #                 .filter(p.timestamp <= end_date)

        query = query1.union(query4) \
            # .union(query3) \
        # .union(query4) \
        # .union(query5) \
        # .union(query6) \
        # .union(query7) \
        # .union(query8) \
        # .union(query9)

        data = pd.DataFrame(query.all())
        data = data.set_index(['device', data.index])
        data = data.sort_index()
        data['delay'] = data.create_dtm - data.timestamp
        # sometime we get slightly negative values because the client and
        # the db server are not time synced. This negative values are set to 0
        data.delay = np.maximum(data.delay, np.timedelta64(0))
        return data


# ----------------------------------------------------------------------------------------------------------------------


class Connectivity(object):
    DEAD_MAN_SWITCH_INTERVAL = timedelta(minutes=1)

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def connection_times(since: datetime, until: datetime, device=None):
        colors = ['#a1eca4', '#ff0000']  # [connected, disconnected]

        dmp = DeadManPackage
        query = db.session.query(dmp.device, dmp.timestamp) \
            .filter(dmp.timestamp >= since) \
            .filter(dmp.timestamp <= until) \
            .filter(dmp.device != "PTL_DEFAULT")

        if device:
            query = query.filter(dmp.device == device)

        data = pd.DataFrame(query.all())

        devices = data.device.unique()
        num_devices = len(devices)
        # add a timestamp for each device at the start of the time interval
        data_since = pd.DataFrame(np.vstack([devices,
                                             np.array(num_devices * [since])])
                                  .transpose(),
                                  columns=["device", "timestamp"])
        # add a timestamp for each device at the end of the time interval
        data_until = pd.DataFrame(np.vstack([devices,
                                             np.array(num_devices * [until])])
                                  .transpose(),
                                  columns=["device", "timestamp"])

        # combine data
        data = pd.concat([data_since, data, data_until], ignore_index=True)

        # compute the time difference between two consecutive rows
        data['delay'] = data.groupby('device').timestamp.diff()
        # The first row for each device has no 'delay' value.
        # We assume this is the start of a connected interval.
        # To do this we set the delay to be bigger than the threshold
        # for data loss
        data = data.fillna(2 * Connectivity.DEAD_MAN_SWITCH_INTERVAL)
        # A data loss happened, if the delay is bigger than a threshold
        # If the row 'connected' contains 1 then no data loss happened at this time
        data['data_loss'] = (data.delay <= 1.5 * Connectivity.DEAD_MAN_SWITCH_INTERVAL).astype(int)
        # compute the difference of consecutive data_loss values to see where
        # the connection status changed
        data['keep_row'] = data.groupby('device').data_loss.diff(periods=-1)
        # We merge intervals of consecutive 'data loss' or 'connection' intervals by
        # keeping only rows where the value of 'keep_rows' is not zero
        data = data[data.keep_row != 0.0]
        # the timestamp row now marks the beginning of an interval where
        # the connection status did not change.
        data = data.rename(columns=dict(timestamp='begin'))
        # compute the duration of each interval
        data['duration'] = data.groupby('device').begin.diff(periods=-1).abs()
        data['end'] = data.begin + data.duration
        data['connected'] = 1 - data.data_loss
        data = data.drop(columns=['delay', 'keep_row', 'data_loss'])
        data['color'] = colors[0]
        data.loc[data.connected == 0, 'color'] = colors[1]
        data = data.dropna()
        data = data.set_index(['device', data.index]).sort_index()

        return data


# ----------------------------------------------------------------------------------------------------------------------


def _timeseries(data, sensor: str):
    expected_signal_interval = timedelta(minutes=10)

    def lost_signal(x):
        return x > expected_signal_interval

    data = pd.DataFrame(data)
    data = data.set_index(['device', data.index])

    devices = data.index.levels[0]
    data_dict = {}
    for device in devices:
        df = data.loc[device]
        df = df.sort_values(by=['timestamp']).dropna()

        # add shifted timestamps as new column
        timestamp_prev = np.asanyarray(df.timestamp.copy())
        timestamp_prev[1:] = timestamp_prev[0:-1]
        df['timestamp_prev'] = timestamp_prev

        # compute time delay between consecutive rows
        df['signal_delay'] = df.timestamp - df.timestamp_prev
        df['lost_signal'] = df.signal_delay.apply(lost_signal)

        data_dict[device] = df[['timestamp', 'signal_delay', 'lost_signal', sensor]].dropna()

    return data_dict


# ----------------------------------------------------------------------------------------------------------------------


def dataframe_from_query(query):
    """Return the result of a SQLAlchemy query as a pandas dataframe"""
    return pd.read_sql(query.statement, query.session.bind)

# ----------------------------------------------------------------------------------------------------------------------

def query_cache(device: str, data_date: Optional[date], query_name: str) -> bool:
    if data_date:
        dfp = DataFramePackage
        query = db.session.query(dfp.id) \
            .filter(dfp.device == device) \
            .filter(dfp.date == data_date) \
            .filter(dfp.query == query_name)
    else:
        dfp = DeviceDataFramePackage
        query = db.session.query(dfp.id) \
            .filter(dfp.device == device) \
            .filter(dfp.query == query_name)

    return query.first() is not None

# ----------------------------------------------------------------------------------------------------------------------


def get_cached_data(device: str, data_date: Optional[date], query_name: str) -> Optional[pd.DataFrame]:
    if data_date:
        dfp = DataFramePackage
        query = db.session.query(dfp.data) \
            .filter(dfp.device == device) \
            .filter(dfp.date == data_date) \
            .filter(dfp.query == query_name)
    else:
        dfp = DeviceDataFramePackage
        query = db.session.query(dfp.data) \
            .filter(dfp.device == device) \
            .filter(dfp.query == query_name)

    data = query.first()
    if data:
        return data[0]

    return None

# ----------------------------------------------------------------------------------------------------------------------


def get_devices():
    def _is_ptl(device):
        if not "PTL" in device:
            return False
        if device == "PTL_DEFAULT" or device == "PTL_UNIT_TEST":
            return False

        return True
    return [device for device in Dashboard().devices() if _is_ptl(device)]

# ----------------------------------------------------------------------------------------------------------------------
