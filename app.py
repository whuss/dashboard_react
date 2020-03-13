import os
import re
import pandas as pd
import numpy as np

from flask import Flask, render_template, jsonify, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_basicauth import BasicAuth
from flask_table import Col, LinkCol, Table
import babel

from bokeh.embed import components
from bokeh.layouts import column
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from typing import Tuple

from dataclasses import dataclass, field
from datetime import datetime, timedelta

import humanfriendly

from plots import plot_histogram, plot_duration_histogram, plot_time_series
from plots import plot_on_off_cycles, plot_lost_signal, plot_crashes, plot_errors
from plots import plot_database_size, plot_error_heatmap, color_palette

import utils

# ----------------------------------------------------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------------------------------------------------


_host: str = "83.175.125.85"
#_host: str = "localhost"
_user: str = "infinity"
_password: str = "iGe9kH9j"
_dbname: str = "bbf_inf_rep"

_db_url: str = f'mysql://{_user}:{_password}@{_host}/{_dbname}'

# ----------------------------------------------------------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------------------------------------------------------


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = _db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BASIC_AUTH_USERNAME'] = "ReproLight"
app.config['BASIC_AUTH_PASSWORD'] = "infinity"
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)

db = SQLAlchemy(app)
db.Model.metadata.reflect(bind=db.engine)

# ----------------------------------------------------------------------------------------------------------------------
# Define DB Model
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

# ----------------------------------------------------------------------------------------------------------------------


class DeviceInfo(db.Model):
    __tablename__ = 'DeviceInfo'
    __table_args__ = dict(extend_existing=True)

    device = db.Column('uk_device_sn', key='device')
    mode = db.Column('device_mode_ind', key='mode')
    last_update = db.Column('last_update_dtm', key='last_update')

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

# ----------------------------------------------------------------------------------------------------------------------


class TemperaturePackage(db.Model):
    __tablename__ = 'TemperaturePackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_temperature_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    temperature = db.Column('temperature_dbl', key='temperature')
    unit = db.Column('unit_sn', key='unit')

# ----------------------------------------------------------------------------------------------------------------------


class HumidityPackage(db.Model):
    __tablename__ = 'HumidityPackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_humidity_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    humidity = db.Column('humidity_dbl', key='humidity')
    unit = db.Column('unit_sn', key='unit')


# ----------------------------------------------------------------------------------------------------------------------


class PressurePackage(db.Model):
    __tablename__ = 'PressurePackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_pressure_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    pressure = db.Column('pressure_dbl', key='pressure')
    unit = db.Column('unit_sn', key='unit')


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

# ----------------------------------------------------------------------------------------------------------------------


class LoudnessPackage(db.Model):
    __tablename__ = 'LoudnessPackage'
    __table_args__ = dict(extend_existing=True)

    id = db.Column('pk_loudness_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    loudness = db.Column('loudness_dbl', key='loudness')
    unit = db.Column('unit_sn', key='unit')

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

    def on_off_timeseries(self, since, until):
        sq_device = self.query_device.subquery()
        ip = InstructionPackage
        sq_on_off = db.session.query(ip.device, ip.service, ip.source, ip.timestamp, ip.instruction, ip.target, ip.value) \
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

        devices = self.query_device.all()
        data_dict = {}
        for device in devices:
            device = device[0]
            df = data.loc[device]
            df = df.sort_values(by=['timestamp'])
            data_dict[device] = df[['timestamp', 'value']].dropna()

        return data_dict

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
        lp = LoggerPackage
        query = db.session \
                  .query(lp.device,
                         lp.timestamp.cast(Date).label('date'),
                         db.func.count(lp.timestamp).label('error_count')) \
                  .filter(lp.log_level == "ERROR") \
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
                  .filter(lp.log_level == "ERROR") \
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
        MAX_LOG_ITEMS_PER_PAGE=50
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
        p = ErrorPackage
        query1 = db.session.query(p.device, p.create_dtm, p.timestamp) \
                        .filter(p.timestamp >= start_date) \
                        .filter(p.timestamp <= end_date)
        p = InstructionPackage
        query2 = db.session.query(p.device, p.create_dtm, p.timestamp) \
                        .filter(p.timestamp >= start_date) \
                        .filter(p.timestamp <= end_date)
        p = LightingPackage
        query3 = db.session.query(p.device, p.create_dtm, p.timestamp) \
                        .filter(p.timestamp >= start_date) \
                        .filter(p.timestamp <= end_date)
        p = MouseGesturePackage
        query4 = db.session.query(p.device, p.create_dtm, p.timestamp) \
                        .filter(p.timestamp >= start_date) \
                        .filter(p.timestamp <= end_date)
        p = TemperaturePackage
        query5 = db.session.query(p.device, p.create_dtm, p.timestamp) \
                        .filter(p.timestamp >= start_date) \
                        .filter(p.timestamp <= end_date)
        p = HumidityPackage
        query6 = db.session.query(p.device, p.create_dtm, p.timestamp) \
                        .filter(p.timestamp >= start_date) \
                        .filter(p.timestamp <= end_date)
        p = PressurePackage
        query7 = db.session.query(p.device, p.create_dtm, p.timestamp) \
                        .filter(p.timestamp >= start_date) \
                        .filter(p.timestamp <= end_date)
        p = GasPackage
        query8 = db.session.query(p.device, p.create_dtm, p.timestamp) \
                        .filter(p.timestamp >= start_date) \
                        .filter(p.timestamp <= end_date)
        p = BrightnessPackage
        query9 = db.session.query(p.device, p.create_dtm, p.timestamp) \
                         .filter(p.timestamp >= start_date) \
                         .filter(p.timestamp <= end_date)
        p = LoudnessPackage
        query10 = db.session.query(p.device, p.create_dtm, p.timestamp) \
                         .filter(p.timestamp >= start_date) \
                         .filter(p.timestamp <= end_date)

        query = query1.union(query2) \
                      .union(query3) \
                      .union(query4) \
                      .union(query5) \
                      .union(query6) \
                      .union(query7) \
                      .union(query8) \
                      .union(query9) \
                      .union(query10) \

        data = pd.DataFrame(query.all())
        data = data.set_index(['device', data.index])
        data = data.sort_index()
        data['delay'] = data.create_dtm - data.timestamp
        # sometime we get slightly negative values because the client and
        # the db server are not time synced. This negative values are set to 0
        data.delay = np.maximum(data.delay, np.timedelta64(0))
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


# ----------------------------------------------------------------------------------------------------------------------
# Jinja customization
# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('datetime')
def format_datetime(value, format='medium'):
    if not value:
        return ""
    if isinstance(value, str):
        value = utils.parse_date(value)

    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="y-MM-dd HH:mm"
    return babel.dates.format_datetime(value, format)

# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('str')
def _str(input):
        return str(input) if input else ""

# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('or_else')
def _or_else(input, else_input):
        return str(input) if input else str(else_input)

# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('timespan')
def _time_span(input):
    if input:
        seconds = input.seconds
        minutes = seconds // 60
        seconds = seconds % 60
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"
        #return humanfriendly.format_timespan(input, max_units=2)
    return ""

# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('none')
def _number(input):
    return input if input else ""

# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('unit')
def _unit(input, unit='°C'):
    if not input:
        return ""
    return f"{input:.2f} {unit}"

# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('format_duration')
def _format_duration(input):
    try:
        minutes = int(input)
        if minutes < 60:
            return f"{minutes} minutes"
        elif minutes % 60 == 0 and minutes // 60 < 24:
            return f"{minutes // 60} hours"
        elif minutes == 60*24:
            return f"1 day"
        else:
            return humanfriendly.format_timespan(timedelta(minutes=minutes), max_units=2)
    except ValueError:
        # input is not an integer
        return str(minutes)

# ----------------------------------------------------------------------------------------------------------------------

#@app.teardown_request
#def teardown(exception=None):
#    # teardown database session
#    session.close()

# ----------------------------------------------------------------------------------------------------------------------


@app.context_processor
def utility_processor():
    def _get_current_page():
        return request.args.get('page', default = 1, type=int)

    def _str(input):
        return str(input) if input else ""

    def _time_span(input):
        if input:
            seconds = input.seconds
            minutes = seconds // 60
            seconds = seconds % 60
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours:02}:{minutes:02}:{seconds:02}"
            #return humanfriendly.format_timespan(input, max_units=2)
        return ""

    def _number(input):
        return input if input else ""

    def _unit(input, unit):
        if not input:
            return ""
        return f"{input:.2f} {unit}"

    return dict(_str=_str,
                _time_span=_time_span,
                _number=_number,
                _unit=_unit,
                get_current_page=_get_current_page)

# ----------------------------------------------------------------------------------------------------------------------<


def url_for_self(**args):
    return url_for(request.endpoint, **dict(request.view_args, **args))

# ----------------------------------------------------------------------------------------------------------------------<


app.jinja_env.globals['url_for_self'] = url_for_self

# ----------------------------------------------------------------------------------------------------------------------<
# Routes
# ----------------------------------------------------------------------------------------------------------------------


@app.route('/')
def index():
    dash = Dashboard()
    start_date = datetime.now() - timedelta(days=1)
    dashboard = dash.dashboard(start_date)
    return render_template('home.html', dashboard=dashboard)

# ----------------------------------------------------------------------------------------------------------------------


class PreCol(Col):
    """Column class for Flask Table that wraps its content in a pre tag"""
    def td_format(self, content):
        return f'''<pre style="text-align: left; width: 75%; white-space: pre-line;">
                       {content}
                   </pre>'''

# ----------------------------------------------------------------------------------------------------------------------


class CrashCol(Col):
    def td_format(self, content):
        c = 'SICK' if content else 'HEALTHY'
        return f'''<i class="fa fa-heartbeat {c}"></i>'''

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/system/crashes/<device>')
def crash_for_device(device):
    data = Errors().crashes(device=device)
    device_data = data.reset_index()

    device_data['formatted_message'] = device_data.apply(format_logentry, axis=1)

    class CrashTable(Table):
        classes = ["error-table"]
        timestamp = LinkCol('Time', 'show_logs',
                            url_kwargs=dict(device='device', timestamp='timestamp'),
                            url_kwargs_extra=dict(duration=5, log_level='TRACE'),
                            attr='timestamp')
        formatted_message = PreCol('Error message')

    table = CrashTable(device_data.to_dict(orient='records'))

    return render_template("crashes_device.html", device=device, table=table)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/system/errors')
def error_statistics():
    error_heatmap = Errors().error_heatmap()
    error_histogram = error_heatmap.groupby(['device', 'date']).error_count.sum().reset_index()

    def _format_next_day(date):
        return (date + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    error_histogram['end_of_day'] = error_histogram.date.apply(_format_next_day)

    # compute time range
    dates = error_histogram.date
    x_range = min(dates), max(dates)

    error_histogram = error_histogram.set_index(['device', 'date'])

    # combute range of y_axis
    y_range = 1, max(error_histogram.error_count)

    error_heatmap['location'] = error_heatmap.apply(lambda row: f"{os.path.basename(row['filename'])}:{row['line_number']}", axis=1)
    # all errors locations in the dataset
    locations = pd.DataFrame(error_heatmap.location.unique(), columns=['location'])
    # assigne a unique color for each error location
    locations['colors'] = color_palette(len(locations.location))
    locations

    eh = error_heatmap.reset_index()
    errors_by_day = eh.drop(columns=['filename', 'line_number']) \
                      .groupby(['device', 'date']) \
                      .sum() \
                      .rename(columns=dict(error_count='errors_by_day'))
    eh = eh.join(errors_by_day, on=['device', 'date'])
    eh['error_count_normalized'] = eh.error_count / eh.errors_by_day
    eh = eh.merge(locations, on = ['location'])
    eh['date_label'] = eh.date
    eh['end_of_day'] = eh.date.apply(_format_next_day)
    eh = eh.set_index(['device', 'date', eh.index]).sort_index()
    error_heatmap = eh

    scripts = []
    data_dict = dict()

    for device in error_histogram.index.levels[0]:
        histogram_data = error_histogram.loc[device].reset_index()
        fig = plot_errors(histogram_data, x_range=x_range, y_range=y_range, device=device)
        fig_heatmap = plot_error_heatmap(error_heatmap.loc[device], x_range=x_range, device=device)
        script, div = components(column(fig, fig_heatmap))
        try:
            total_number_of_errors = histogram_data.error_count.sum()
        except KeyError:
            total_number_of_errors = 0
        data_dict[device] = dict(total_number_of_errors=total_number_of_errors,
                                 plot=div)
        scripts.append(script)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    return render_template("error_statistics.html",
                           route='/system/errors',
                           data=data_dict,
                           scripts=scripts,
                           js_resources=js_resources,
                           css_resources=css_resources)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/system/error_heatmap')
def error_heatmap():
    data = Errors().error_heatmap()
    data['location'] = data.apply(lambda row: f"{os.path.basename(row['filename'])}:{row['line_number']}", axis=1)

    class HeatmapTable(Table):
        classes = ["error-table"]
        date = LinkCol('Date', 'show_logs',
                       url_kwargs=dict(device='device',
                                       timestamp='end_of_day',
                                       filename='filename',
                                       line_number='line_number'),
                       url_kwargs_extra=dict(log_level='ERROR', duration=60*24), attr="date")
        location = Col("Location")
        error_count = Col("Error count")

    data_dict = dict()

    for device in data.index.levels[0]:
        device_data = data.loc[device] \
                          .reset_index() \
                          .sort_values(by='date', ascending=False)
        device_data['device'] = device
        data_dict[device] = HeatmapTable(device_data.to_dict(orient='records'))

    return render_template("errors.html", route='/system/errors', data=data_dict, messages="Errors by file location")

# ----------------------------------------------------------------------------------------------------------------------

@app.route('/system/crashes')
def crashes():
    crash_data = Errors().crashes()
    crash_histogram = crash_data.reset_index()
    crash_histogram = crash_histogram.drop(columns=['source', 'filename', 'line_number', 'log_level', 'message'])
    crash_histogram['date'] = crash_histogram.timestamp.apply(lambda x: x.date())
    crash_histogram = crash_histogram.drop(columns=['timestamp'])
    crash_histogram = crash_histogram.groupby(['device', 'date']).count()
    crash_histogram = crash_histogram.rename(columns=dict(level_1="crash_count"))
    crash_histogram = crash_histogram.reset_index()
    crash_histogram = crash_histogram.set_index(['device', 'date'])

    version_data = Errors().version()
    version_histogram = version_data.reset_index()
    version_histogram = version_histogram.drop(columns=['version_timestamp', 'branch', 'commit', 'ip'])
    version_histogram['date'] = version_histogram.timestamp.apply(lambda x: x.date())
    version_histogram = version_histogram.drop(columns=['timestamp'])
    version_histogram = version_histogram.groupby(['device', 'date']).count()
    version_histogram = version_histogram.rename(columns=dict(level_1="restart_count"))
    version_histogram = version_histogram.reset_index()
    version_histogram = version_histogram.set_index(['device', 'date'])

    combined_histogram = pd.merge(crash_histogram, version_histogram,
                                  left_index=True, right_index=True, how="outer") \
                           .fillna(value=0)

    combined_histogram.crash_count = combined_histogram.crash_count.astype('int')
    combined_histogram.restart_count = combined_histogram.restart_count.astype('int')

    # compute string of the end of the day for url creation
    def end_of_day(row):
        date = row.name[1]
        return (date + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

    combined_histogram['end_of_day'] = combined_histogram.apply(end_of_day, axis=1)

    # compute time range
    dates = combined_histogram.reset_index().date
    x_range = min(dates), max(dates)

    # combute range of y_axis
    y_range = 0, max(max(version_histogram.restart_count), max(crash_histogram.crash_count))

    scripts = []
    data_dict = dict()

    for device in combined_histogram.index.levels[0]:
        histogram_data = combined_histogram.loc[device].reset_index()
        fig = plot_crashes(histogram_data, x_range=x_range, y_range=y_range, device=device)
        script, div = components(fig)
        try:
            total_number_of_crashes = len(crash_data.loc[device])
        except KeyError:
            total_number_of_crashes = 0
        try:
            total_number_of_restarts = len(version_data.loc[device])
        except KeyError:
            total_number_of_restarts = 0
        data_dict[device] = dict(total_number_of_crashes=total_number_of_crashes,
                                 total_number_of_restarts=total_number_of_restarts,
                                 plot=div)
        scripts.append(script)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    return render_template("crashes.html",
                           route='/system/crashes',
                           data=data_dict,
                           scripts=scripts,
                           js_resources=js_resources,
                           css_resources=css_resources)

# ----------------------------------------------------------------------------------------------------------------------


def _logs(device_id, timestamp, log_level="TRACE", before=2, after=2, page=None, filename=None, line_number=None):
    restart_time = utils.parse_date(timestamp)
    start_date = restart_time - timedelta(minutes=before)
    end_date = restart_time + timedelta(minutes=after)

    logs, pagination = Errors().logs(device_id=device_id, log_level=log_level, since=start_date, until=end_date,
                                     page=page, filename=filename, line_number=line_number)
    if not logs.empty:
        log_text = format_logs(logs, device=device_id)
    else:
        log_text = "No logs available."
    return log_text, pagination

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/logs/<device>', methods=['GET'])
@app.route('/logs/<device>/<int:duration>', methods=['GET'])
@app.route('/logs/<device>/<int:duration>/<log_level>', methods=['GET'])
@app.route('/logs/<device>/<int:duration>/<log_level>/<timestamp>/', methods=['GET'])
def show_logs(device, duration=5, timestamp=None, log_level="TRACE"):
    try:
        page = int(request.args.get('page', default=1, type=int))
    except ValueError:
        print(f"get value page={page} is not an integer")
        page = 1

    filename = request.args.get('filename', default=None)
    line_number = request.args.get('line_number', type=int, default=None)

    if not timestamp:
        timestamp = datetime.now()
    log_text, pagination = _logs(device, timestamp, log_level, before=duration, after=2, page=page,
                                 filename=filename, line_number=line_number)
    devices = Dashboard().devices()
    return render_template("device_log.html", devices=devices, log_text=log_text, device=device, pagination=pagination)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/system/version', methods=['GET'])
def version_messages():
    device_id = request.args.get('id', default = "", type = str)
    errors = Errors()
    data = errors.version(device_id=device_id)

    class VersionTable(Table):
        classes = ["error-table"]
        timestamp = LinkCol('Time', 'show_logs',
                            url_kwargs=dict(device='device', timestamp='timestamp'),
                            url_kwargs_extra=dict(log_level='TRACE', duration=5),
                            attr='timestamp')
        ip = Col('IP Address')
        commit = Col('Commit')
        branch = Col('branch')
        version_timestamp = Col('Version Timestamp')
        crash = CrashCol('Crash')

    data_dict = dict()

    for device in data.index.levels[0]:
        device_data = data.loc[device] \
                          .sort_values(by='timestamp', ascending=False)
        device_data['device'] = device
        data_dict[device] = VersionTable(device_data.to_dict(orient='records'))

    return render_template("errors.html", route='/system/version', data=data_dict, messages="System start")

# ----------------------------------------------------------------------------------------------------------------------

trace_re = re.compile("(.*) \[(.+):(\d+)\]")

def format_logentry(lp, device=None):
    # This is obsolete, and only needed for old log entries
    # Trace log entries get correctly formatted since commit a30b3b5e2afc1b5a7c5790e0f53596cf8c9f80d4
    if lp.log_level == "TRACE":
        match = trace_re.match(lp.message)
        if match:
            lp.message = match.group(1)
            lp.filename = match.group(2)
            lp.line_number = int(match.group(3))

    filename = os.path.basename(lp.filename)
    location = f"[{filename}:{lp.line_number}]:"
    time = lp.timestamp.strftime('%Y-%m-%d %H:%M:%S')

    if filename == "watchdog.py" and lp.log_level == "INFO":
        log_level_class = "WATCHDOG_INFO"
    else:
        log_level_class = lp.log_level

    if device:
        log_url = url_for('show_logs', device=device, duration=1, log_level="TRACE", timestamp=time)
        time_format = f'<a href="{log_url}">{time}</a>'
    else:
        time_format = time

    header_no_format = f'({time}) {lp.log_level:<8} {location:>25} '
    header = f'({time_format}) <span class="{log_level_class}">{lp.log_level:<8}</span> ' \
                f'<span class="log-filename" data-toggle="tooltip" title="{lp.filename}:{lp.line_number}" >' \
                f'{location:>25}</span> '
    identation = len(header_no_format) * " "
    message_lines = lp.message.split("\n")
    formatted_message = header + message_lines[0] + "\n" + \
        "\n".join([identation + line for line in message_lines[1:]])

    if len(message_lines) > 1:
        formatted_message += "\n"

    return formatted_message

# ----------------------------------------------------------------------------------------------------------------------


def format_logs(logs, device=None):
    log_text = ""
    for index, lp in logs.iterrows():
        log_text += format_logentry(lp, device)

    return log_text

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/_monitor_device', methods=['POST'])
def _monitor_device():
    device = ""
    limit = False
    log_level = "TRACE"
    if request.method == 'POST':
        device = request.form.get('device')
        limit = request.form.get('limit')
        log_level = request.form.get('log_level')
        if limit == "true":
            limit = True
        else:
            limit = False

    print(f"_monitor: device={device}, limit={limit}, log_level={log_level}")
    if limit == True:
        num_lines = 35
    else:
        num_lines = 50000

    start_date = datetime.now() - timedelta(days=1)
    logs, pagination = Errors().logs(device_id=device, since=start_date, num_lines=num_lines, log_level=log_level)

    log_text = format_logs(logs, device=device)

    if limit:
        title = f"Start monitoring device {device} ..."
    else:
        title = f"Load logs for device {device} ..."

    return jsonify(title=title, result=f"<pre>{log_text}</pre>")

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/monitor')
def monitor():
    devices = Dashboard().devices()
    for device in devices:
        print(device)
    return render_template("monitor.html", devices=devices)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/statistics/mode')
def statistics_mode():
    data = ModeStatistics().mode_counts()
    labels = ["Auto", "Off", "Manual", "Light Shower"]
    return render_template('statistics_mode.html', data=data, labels=jsonify(labels))

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/statistics/mouse', methods=['GET'])
def statistics_mouse():
    start_date, end_date = parse_date_range(request)
    no_data = dict(stats="", plot_distance="", plot_speed="", plot_deviation="")

    mouse_data = MouseData().gesture_data(start_date, end_date)

    statistics_data = {}
    scripts = []
    for device, data in mouse_data.items():
        if data.count()[0] > 0:
            fig_distance = plot_histogram(data.distance.dropna(),
                x_axis_label="Mouse distance", y_axis_label="Amount",
                plot_width=300, plot_height=400
            )
            script, div_distance = components(fig_distance)
            scripts.append(script)

            fig_speed = plot_histogram(data.speed.dropna(),
                x_axis_label="Mouse speed", y_axis_label="Amount",
                plot_width=300, plot_height=400, fill_color='blue'
            )
            script, div_speed = components(fig_speed)
            scripts.append(script)

            fig_deviation = plot_histogram(data.deviation.dropna(),
                x_axis_label="Gesture deviation", y_axis_label="Amount",
                plot_width=300, plot_height=400, fill_color='orange'
            )
            script, div_deviation = components(fig_deviation)
            scripts.append(script)


            stats = data.describe().to_html()
            statistics_data[device] = dict(stats=stats,
                                      plot_distance=div_distance,
                                      plot_speed=div_speed,
                                      plot_deviation=div_deviation)

        else:
            statistics_data[device] = no_data

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    return render_template("statistics_mouse.html",
                           timespan=humanfriendly.format_timespan(end_date-start_date, max_units=2),
                           data=statistics_data,
                           scripts=scripts,
                           js_resources=js_resources,
                           css_resources=css_resources)

# ----------------------------------------------------------------------------------------------------------------------

def parse_date_range(request):
    start_str = request.args.get('start', default = "", type = str)
    end_str = request.args.get('end', default = "", type = str)
    from dateutil.parser import parse

    if not end_str:
        end_date = datetime.now()
    else:
        end_date = parse(end_str)

    if not start_str:
        start_date = end_date - timedelta(days=1)
    else:
        start_date = parse(start_str)

    print(f"Date range: {start_str} -- {end_str}")
    print(f"Parsed Date range: {start_date} -- {end_date}")
    return (start_date, end_date)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/statistics/database_delay', methods=['GET'])
def statistics_database_delay():
    start_date, end_date = parse_date_range(request)
    data = DatabaseDelay().package_delay(start_date, end_date)

    print("Query finished")

    figures = {}
    scripts = []

    # compute time range
    x_range = min(data.delay), max(data.delay)

    for device in data.index.levels[0]:
        device_data = data.loc[device].delay.dropna()

        total_packages = device_data.count()

        fig = plot_duration_histogram(device_data, time_scale="s",
                x_axis_label="Package delay", y_axis_label="Amount",
                plot_width=600, plot_height=400
            )
        script, div = components(fig)
        figures[device] = dict(div=div, total_packages=total_packages)
        scripts.append(script)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    return render_template("statistics_database_delay.html",
                           timespan=humanfriendly.format_timespan(end_date-start_date, max_units=2),
                           figures=figures,
                           scripts=scripts,
                           js_resources=js_resources,
                           css_resources=css_resources)

# ----------------------------------------------------------------------------------------------------------------------

@app.route('/database/size')
def database_size():
    data = DatabaseDelay().size()

    fig = plot_database_size(data)

    script, div = components(fig)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    return render_template("database_size.html",
                           figure=div,
                           script=script,
                           js_resources=js_resources,
                           css_resources=css_resources)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/statistics/switch_cycles')
def statistics_switch_cycles():
    data = PresenceDetectorStatistics().on_off_cycle_count()

    figures = {}
    scripts = []

    # compute time range
    dates = data.reset_index().date
    x_range = min(dates) - timedelta(days=1), max(dates) + timedelta(days=1)

    for device in data.index.levels[0]:
        device_data = data.loc[device].reset_index()
        fig = plot_on_off_cycles(device_data, x_range=x_range)
        script, div = components(fig)
        figures[device] = div
        scripts.append(script)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    return render_template("statistics_on_off.html",
                           figures=figures,
                           scripts=scripts,
                           js_resources=js_resources,
                           css_resources=css_resources)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors')
def sensors():
    sensor_data = SensorData().current_sensor_data()

    return render_template('sensors.html', sensors=sensor_data)

# ----------------------------------------------------------------------------------------------------------------------


def create_timeseries(sensor_data, sensor: str, unit: str, time_range: Tuple[datetime, datetime], **kwargs):
    # If no sensor_key is given, use the lower case sensor name
    sensor_key = kwargs.pop("sensor_key", sensor).lower()
    start_date, end_date = time_range
    plot_scripts = {}
    plot_divs = {}
    x_range = (start_date, end_date)
    for device, data in sensor_data.items():
        if not data.empty:
            fig = plot_time_series(data.timestamp,
                                   data[[sensor_key]].iloc[:, 0],
                                   x_range=x_range,
                                   y_axis_label=unit,
                                   mode='step')
            script, div = components(fig)
        else:
            script, div = "", ""
        plot_scripts[device] = script
        plot_divs[device] = div

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    html = render_template(
        'sensors_timeseries.html',
        timespan=humanfriendly.format_timespan(end_date-start_date, max_units=2),
        sensor=sensor,
        unit=unit,
        plot_scripts=plot_scripts,
        plot_divs=plot_divs,
        js_resources=js_resources,
        css_resources=css_resources,
    )

    return encode_utf8(html)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/device/<device>', methods=['GET'])
def sensors_device(device):
    start_date, end_date = parse_date_range(request)
    x_range = (start_date, end_date)
    figures = {}
    sensor = SensorData()

    #sensor_data = PresenceDetectorStatistics().on_off_timeseries(start_date, end_date, device)
    #fig = plot_time_series(sensor_data.timestamp, sensor_data.value, x_range=x_range, mode="step")
    #x_range = fig.x_range
    #figures['on_off'] = fig

    sensor_data = sensor.temperature(start_date, end_date, device)[device]
    fig = plot_time_series(sensor_data.timestamp,
                           sensor_data.temperature,
                           x_range=x_range,
                           title="Temperature",
                           y_axis_label="°C")
    x_range = fig.x_range
    figures['temperature'] = fig

    sensor_data = sensor.humidity(start_date, end_date, device)[device]
    fig = plot_time_series(sensor_data.timestamp,
                           sensor_data.humidity,
                           x_range=x_range,
                           title="Humidity",
                           y_axis_label="%RH")
    figures['humidity'] = fig

    sensor_data = sensor.pressure(start_date, end_date, device)[device]
    fig = plot_time_series(sensor_data.timestamp,
                           sensor_data.pressure,
                           x_range=x_range,
                           title="Pressure",
                           y_axis_label="hPa")
    figures['pressure'] = fig

    sensor_data = sensor.brightness(start_date, end_date, device).loc[device]
    figures_brightness = timeseries_plot_brightness(sensor_data,
                                                    unit="lx",
                                                    x_range=x_range)

    for key, fig in figures_brightness.items():
        figures[key] = fig

    sensor_data = sensor.gas(start_date, end_date, device)[device]
    fig = plot_time_series(sensor_data.timestamp,
                           sensor_data.amount,
                           x_range=x_range,
                           title="Gas (VOC)",
                           y_axis_label="kOhm")
    figures['gas'] = fig

    plot = column(*list(figures.values()))

    #plot = column(figures['temperature'],
    #              figures['humidity'],
    #              figures['pressure'],
    #              figures['gas'])
    plot_scripts, plot_divs = components(plot)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    html = render_template(
        'device_sensors_timeseries.html',
        timespan=humanfriendly.format_timespan(end_date-start_date, max_units=2),
        device=device,
        plot_scripts=plot_scripts,
        plot_divs=plot_divs,
        js_resources=js_resources,
        css_resources=css_resources,
    )

    return encode_utf8(html)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/presence', methods=['GET'])
def sensors_presence():
    start_date, end_date = parse_date_range(request)
    on_off_data = PresenceDetectorStatistics().on_off_timeseries(start_date, end_date)

    return create_timeseries(on_off_data, sensor="Presence detected",
                             sensor_key="value",
                             unit="off=0, on=1", time_range=(start_date, end_date), mode="step")

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/temperature', methods=['GET'])
def sensors_temp():
    start_date, end_date = parse_date_range(request)
    sensor_data = SensorData().temperature(start_date, end_date)

    return create_timeseries(sensor_data, sensor="Temperature", unit="°C", time_range=(start_date, end_date))

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/humidity', methods=['GET'])
def sensors_humidity():
    start_date, end_date = parse_date_range(request)
    sensor_data = SensorData().humidity(start_date, end_date)

    return create_timeseries(sensor_data, sensor="Humidity", unit="%RH", time_range=(start_date, end_date))

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/pressure', methods=['GET'])
def sensors_pressure():
    start_date, end_date = parse_date_range(request)
    sensor_data = SensorData().pressure(start_date, end_date)

    return create_timeseries(sensor_data, sensor="Pressure", unit="hPa", time_range=(start_date, end_date))

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/gas', methods=['GET'])
def sensors_gas():
    start_date, end_date = parse_date_range(request)
    sensor_data = SensorData().gas(start_date, end_date)

    return create_timeseries(sensor_data, sensor="Gas", sensor_key="amount", unit="VOC kOhm", time_range=(start_date, end_date))

# ----------------------------------------------------------------------------------------------------------------------


def timeseries_plot_brightness(device_data, unit: str, x_range, **kwargs):
    sensor_id_dict = {"brightness_r_h@BH1750": "RH",
                      "brightness_r_v@BH1750": "RV",
                      "brightness_l_h@BH1750": "LH",
                      "brightness_l_v@BH1750": "LV"}
    device_data = device_data.dropna()

    # re-index the data set of each single device
    # so that sensor_ids only contains items that are
    # included in the data set of this particular device
    device_data = device_data.set_index(device_data.index)
    sensor_ids = device_data.index.levels[0]
    figures = {}
    # loop over all 4 brightness sensors
    # if data for this sensor is available
    for sensor_id in sensor_ids:
        data = device_data.loc[sensor_id]
        data = data.sort_values(by=['timestamp'])

        time_series = data.brightness
        timestamp = data.timestamp

        # Convert sensor name to shorter form
        sensor_name = sensor_id_dict.get(sensor_id, sensor_id)

        fig = plot_time_series(timestamp, time_series,
                               x_range=x_range,
                               title=f"Brightness ({sensor_name})", y_axis_label=unit)
        x_range = fig.x_range

        figures[f'brightness_{sensor_name}'] = fig

    return figures

# ----------------------------------------------------------------------------------------------------------------------


def create_timeseries_brightness(sensor_data, sensor: str, unit: str, time_range: Tuple[datetime, datetime], **kwargs):
    sensor_id_dict = {"brightness_r_h@BH1750": "RH",
                          "brightness_r_v@BH1750": "RV",
                          "brightness_l_h@BH1750": "LH",
                          "brightness_l_v@BH1750": "LV"}

    # If no sensor_key is given, use the lower case sensor name
    sensor_key = kwargs.get("sensor_key", sensor).lower()
    start_date, end_date = time_range
    plot_scripts = {}
    plot_divs = {}

    # loop over all devices
    devices = sensor_data.index.levels[0]
    for device in devices:
        device_data = sensor_data.loc[device].dropna()
        script, div = "", ""

        # re-index the data set of each single device
        # so that sensor_ids only contains items that are
        # included in the data set of this particular device
        device_data = device_data.set_index(device_data.index)
        sensor_ids = device_data.index.levels[0]
        figures = []
        x_range = None
        # loop over all 4 brightness sensors
        # if data for this sensor is available
        for sensor_id in sensor_ids:
            if not x_range:
                x_range = (start_date, end_date)
            data = device_data.loc[sensor_id]
            data = data.sort_values(by=['timestamp'])

            time_series = data[[sensor_key]].iloc[:, 0]
            timestamp = data.timestamp

            # Convert sensor name to shorter form
            sensor_name = sensor_id_dict.get(sensor_id, sensor_id)

            fig = plot_time_series(timestamp, time_series,
                                   x_range=x_range,
                                   title=f"Sensor: {sensor_name}")
            x_range = fig.x_range

            figures.append(fig)

        plot = column(*figures)
        _script, _div = components(plot)
        script += _script
        div += _div

        plot_scripts[device] = script
        plot_divs[device] = div

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    html = render_template(
        'sensors_timeseries.html',
        timespan=humanfriendly.format_timespan(end_date-start_date, max_units=2),
        sensor=sensor,
        unit=unit,
        plot_scripts=plot_scripts,
        plot_divs=plot_divs,
        js_resources=js_resources,
        css_resources=css_resources,
    )

    return encode_utf8(html)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/brightness', methods=['GET'])
def sensors_brightness():
    start_date, end_date = parse_date_range(request)
    sensor_data = SensorData().brightness(start_date, end_date)

    return create_timeseries_brightness(sensor_data, sensor="Brightness", unit="lx", time_range=(start_date, end_date))

# ----------------------------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)
