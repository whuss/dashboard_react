from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import utils

# ----------------------------------------------------------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------------------------------------------------------


db = SQLAlchemy()

# ----------------------------------------------------------------------------------------------------------------------
# Define DB Model
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
    create_dtm = db.Column('create_dtm')

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
    def getColumns(self):
        return self.__table__.columns

    # ------------------------------------------------------------------------------------------------------------------

    def getColumnNames(self):
        return self.getColumns().keys()

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

    def query_light(self, start_date):
        """number of lighting changes since start_date per PTL-device"""
        lp = LightingPackage
        light_count = db.func.count(lp.id).label('light_count')
        return db.session.query(lp.device, light_count) \
                      .filter(lp.timestamp >= start_date) \
                      .group_by(lp.device)

    # ------------------------------------------------------------------------------------------------------------------

    def query_mouse(self, start_date):
        """number of mouse gestures since start_date per PTL-device"""
        mp = MouseGesturePackage
        mouse_count = db.func.count(mp.id).label('mouse_count')
        return db.session.query(mp.device, mouse_count) \
                      .filter(mp.timestamp >= start_date) \
                      .group_by(mp.device)

    # ------------------------------------------------------------------------------------------------------------------

    def query_last_connection(self, start_date):
        tp = TemperaturePackage
        last_connection = db.func.max(tp.id).label('last_index')
        last_index = db.session.query(tp.device, last_connection) \
                       .group_by(tp.device) \
                       .subquery()

        return db.session.query(tp.device, tp.id, tp.timestamp.label('last_update')) \
                 .join(last_index, tp.id == last_index.c.last_index)

    # ------------------------------------------------------------------------------------------------------------------

    def query_dashboard(self, start_date):
        """database query for main information dashboard"""
        sq_mode = self.query_mode.subquery()
        sq_last_connection = self.query_last_connection(start_date).subquery()

        since = db.func.timediff(db.func.now(), sq_mode.c.timestamp).label('since')

        return self.query_info \
                   .outerjoin(sq_mode, DeviceInfo.device == sq_mode.c.device) \
                   .outerjoin(sq_last_connection, DeviceInfo.device == sq_last_connection.c.device) \
                   .add_columns(sq_mode.c.mode,
                                since,
                                sq_last_connection.c.last_update) \
                   .order_by(DeviceInfo.device)

    # ------------------------------------------------------------------------------------------------------------------

    def dashboard(self, start_date):
        query = self.query_dashboard(start_date)
        return query.all()

    # ------------------------------------------------------------------------------------------------------------------

    def info(self):
        query_device = db.session.query(DeviceInfo.device, DeviceInfo.mode.label('study_mode')) \
            .order_by(DeviceInfo.device) \
            .filter(DeviceInfo.device != "PTL_DEFAULT")

        dmp = DeadManPackage
        sq_connection = db.session.query(dmp.device, db.func.max(dmp.timestamp).label('last_connection')) \
            .group_by(dmp.device) \
            .filter(DeviceInfo.device != "PTL_DEFAULT") \
            .subquery()

        query = query_device.outerjoin(sq_connection, sq_connection.c.device == DeviceInfo.device) \
            .add_columns(sq_connection.c.last_connection)

        data = pd.DataFrame(query.all())
        now = datetime.now()
        data['offline_duration'] = data.last_connection.apply(lambda x: now - x)

        def health_status(offline_duration):
            if offline_duration < timedelta(minutes=2):
                return "HEALTHY"
            else:
                return "SICK"

        data['health_status'] = data.offline_duration.apply(health_status)

        def sick_reason(row):
            if pd.isna(row.last_connection):
                return "Never online"

            if row.health_status == "SICK":
                return f"Offline for {row.offline_duration}"
            else:
                return ""

        data['sick_reason'] = data.apply(sick_reason, axis=1)

        return data

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

    def temperature(self, since, until, device=None):
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

    def brightness(self, since, until, device=None):
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

    def humidity(self, since, until, device=None):
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

    def pressure(self, since, until, device=None):
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

    def gas(self, since, until, device=None):
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

    def _on_off(self, x):
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
        data.value = data.value.apply(self._on_off)
        data = data.set_index(['device', data.index])

        return data

    # ------------------------------------------------------------------------------------------------------------------

    def on_off_timeseries(self, since, until, device=None):
        ip = InstructionPackage
        query = db.session.query(ip.device, ip.timestamp, ip.value) \
            .filter(ip.source.contains("Lullaby")) \
            .filter(ip.instruction == "MODE") \
            .filter(ip.target == "POWER") \
            .filter(ip.timestamp >= since) \
            .filter(ip.timestamp <= until) \
            .order_by(ip.device, ip.timestamp)

        if device:
            query = query.filter(ip.device == device)

        data = pd.DataFrame(query.all())
        if data.empty:
            return data

        data.value = data.value.apply(self._on_off)

        # remove consecutive rows with the same 'value'
        data['keep_row'] = data.groupby('device').value.diff(periods=1)
        data = data[data.keep_row != 0.0]
        # merge intervals, such that each row in the data corresponds to one
        # interval ['begin', 'end'] where the light has been either on ('value'=1)
        # or off ('value' = 0) the whole time.
        data = data.rename(columns=dict(timestamp='begin'))
        data['duration'] = data.groupby('device').begin.diff(periods=-1).abs()
        data['end'] = data.begin + data.duration

        data = data.set_index(['device', data.index])
        return data

    # ------------------------------------------------------------------------------------------------------------------

    def on_off_cycle_count(self):
        ip = InstructionPackage
        sq_device = db.session.query(DeviceInfo.device).subquery()

        query = db.session.query(ip.device, ip.source, ip.timestamp, ip.instruction, ip.target, ip.value) \
                    .filter(ip.source.contains("Lullaby")) \
                    .filter(ip.instruction == "MODE") \
                    .filter(ip.target == "POWER") \
                    .filter(ip.value == "ON") \
                    .filter(ip.device != "PTL_DEFAULT") \
                    .outerjoin(sq_device, sq_device.c.device == ip.device) \
                    .order_by(ip.device)

        def is_night(date):
            time = date.time()
            return time.hour <= 6 or time.hour >= 22

        data = pd.DataFrame(query.all())
        data = data.drop(columns=['source', 'target', 'instruction'])
        data['date'] = data.timestamp.apply(lambda x: x.date())
        data['night'] = data.timestamp.apply(is_night)
        data = data.set_index(['device', 'date', 'night', data.index])
        data = data.groupby(['device', 'date', 'night']).count()
        data = data.drop(columns=['timestamp'])
        data = data.rename(columns=dict(value="count"))
        return data

# ----------------------------------------------------------------------------------------------------------------------


class Errors(object):
    def crashes(self, device=None):
        lp = LoggerPackage
        query = db.session.query(lp.device, lp.source, lp.timestamp, lp.filename, lp.line_number, lp.log_level, lp.message) \
                          .filter(lp.log_level == "CRITICAL")

        if device:
            query = query.filter(lp.device == device)

        query = query.filter(lp.device != "PTL_DEFAULT")

        data = pd.DataFrame(query.all())

        data = data.set_index(['device', data.index])
        return data

    # ------------------------------------------------------------------------------------------------------------------

    def crash_histogram(self):
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
        data = data.set_index(['device', 'date'])
        return data

    # ------------------------------------------------------------------------------------------------------------------

    def restart_histogram(self):
        from sqlalchemy import Date
        vp = VersionPackage
        query = db.session \
            .query(vp.device,
                   vp.timestamp.cast(Date).label('date'),
                   db.func.count(vp.timestamp).label('restart_count')) \
            .filter(vp.device != "PTL_DEFAULT") \
            .group_by('date') \
            .group_by(vp.device)

        data = pd.DataFrame(query.all())
        data = data.set_index(['device', 'date'])
        return data

    # ------------------------------------------------------------------------------------------------------------------

    def errors(self, device=None):
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

    def error_histogram(self):
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

        data=pd.DataFrame(query.all())
        data['end_of_day'] = data.date.apply(lambda x: x + timedelta(days=1))
        data = data.set_index(['device', 'date'])
        return data

    # ------------------------------------------------------------------------------------------------------------------

    def error_heatmap(self):
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

    def crash_at_time(self, device, time):
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

    def logs(self, device_id=None, since=None, until=None, num_lines=None, log_level="TRACE", page=None,
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

        query = db.session.query(lp.device, lp.source, lp.timestamp, lp.filename, lp.line_number, lp.log_level, lp.message) \
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
                filter = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
            elif log_level == "INFO":
                filter = ["CRITICAL", "ERROR", "WARNING", "INFO"]
            elif log_level == "WARNING":
                filter = ["CRITICAL", "ERROR", "WARNING"]
            elif log_level == "ERROR":
                filter = ["CRITICAL", "ERROR"]
            elif log_level == "CRITICAL":
                filter = ["CRITICAL"]
            else:
                filter = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE"]

            query = query.filter(lp.log_level.in_(filter))

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

    def version(self, device_id=None, check_crashes=True):
        vp = VersionPackage

        sq_device = db.session.query(DeviceInfo.device).subquery()

        query = db.session.query(vp.device, vp.timestamp, vp.version_timestamp, vp.branch, vp.commit, vp.ip) \
                       .outerjoin(sq_device, sq_device.c.device == vp.device) \
                       .order_by(vp.device)

        query = query.filter(vp.device != "PTL_DEFAULT")

        if device_id:
            query = query.filter(vp.device == device_id)

        data = pd.DataFrame(query.all())

        if check_crashes:
            data['crash'] = data.apply(lambda row: self.crash_at_time(row['device'], row['timestamp']), axis=1)

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

    def _table_to_python(self, table):
        data = {}
        for row in table:
            if row.device not in data:
                data[row.device] = ModeStatistics.ModeCounts(device=row.device)
            if row.mode:
                setattr(data[row.device], row.mode.lower(), row.count)
        return sorted(data.values())

    # ------------------------------------------------------------------------------------------------------------------

    def mode_counts(self):
        return self._table_to_python(self.query_mode.all())

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

    def size(self):
        dp = DbSizePackage
        query = db.session.query(dp.date, dp.data_size_in_mb, dp.index_size_in_mb)
        data = pd.DataFrame(query.all())

        data['total_size'] = data.data_size_in_mb + data.index_size_in_mb

        return data

    # ------------------------------------------------------------------------------------------------------------------

    def package_delay(self, start_date, end_date):
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
                      #.union(query3) \
                      #.union(query4) \
                      #.union(query5) \
                      #.union(query6) \
                      #.union(query7) \
                      #.union(query8) \
                      #.union(query9)

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
        return (x > expected_signal_interval)

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
