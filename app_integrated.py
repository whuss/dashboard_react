import os
import re
import pandas as pd
import numpy as np

from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table
from sqlalchemy.event import listens_for
from flask_table import Col, LinkCol # Table
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
from plots import plot_on_off_cycles, plot_lost_signal

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
db = SQLAlchemy(app)
db.Model.metadata.reflect(bind=db.engine)

# ----------------------------------------------------------------------------------------------------------------------
# Define DB Model
# ----------------------------------------------------------------------------------------------------------------------

@listens_for(Table, "column_reflect")
def column_reflect(inspector, table, column_info):
    print(column_info)
    # set column.key = "attr_<lower_case_name>"
    column_info['key'] = "attr_%s" % column_info['name'].lower()


class DeviceInfo(db.Model):
    __table__ = db.Model.metadata.tables['DeviceInfo']
    __table_args__ = dict(autoload=True)

    device = __table__.c.uk_device_sn
    mode = __table__.c.device_mode_ind
    last_update = __table__.c.last_update_dtm

# ----------------------------------------------------------------------------------------------------------------------


class ErrorPackage(db.Model):
    __table__ = db.Model.metadata.tables['ErrorPackage']
    __table_args__ = dict(autoload=True)

    id = __table__.c.pk_error_package_id
    device = __table__.c.ix_device_sn
    service = __table__.c.service_sn
    source = __table__.c.ix_source_sn
    timestamp = __table__.c.ix_data_dtm
    errno = __table__.c.number_int
    message = __table__.c.message_str

# ----------------------------------------------------------------------------------------------------------------------


class LoggerPackage(db.Model):
    __table__ = db.Model.metadata.tables['LoggerPackage']
    __table_args__ = dict(autoload=True)

    id = __table__.c.pk_logger_package_id
    device = __table__.c.ix_device_sn
    service = __table__.c.service_sn
    source = __table__.c.ix_source_sn
    timestamp = __table__.c.ix_data_dtm
    filename = __table__.c.filename_str
    line_number = __table__.c.line_number_int
    log_level = __table__.c.log_level_ind
    message = __table__.c.message_str

# ----------------------------------------------------------------------------------------------------------------------


class VersionPackage(db.Model):
    __table__ = db.Model.metadata.tables['VersionPackage']
    __table_args__ = dict(autoload=True)

    id = __table__.c.pk_version_package
    device = __table__.c.ix_device_sn
    service = __table__.c.service_sn
    source = __table__.c.ix_source_sn
    timestamp = __table__.c.ix_data_dtm
    commit = __table__.c.commit_sn
    branch = __table__.c.branch_sn
    version_timestamp = __table__.c.version_timestamp_dtm

# ----------------------------------------------------------------------------------------------------------------------


class InstructionPackage(db.Model):
    __table__ = db.Model.metadata.tables['InstructionPackage']
    __table_args__ = dict(autoload=True)

    id = __table__.c.pk_instruction_package_id
    device = __table__.c.ix_device_sn
    service = __table__.c.service_sn
    source = __table__.c.ix_source_sn
    timestamp = __table__.c.ix_data_dtm
    instruction = __table__.c.instruction_ind
    target = __table__.c.target_ind
    value = __table__.c.value_jsn

    # ------------------------------------------------------------------------------------------------------------------

    # FIXME: make static, get mapped column names
    def getColumns(self):
        return self.__table__.columns

    # ------------------------------------------------------------------------------------------------------------------

    def getColumnNames(self):
        return self.getColumns().keys()

# ----------------------------------------------------------------------------------------------------------------------


class LightingPackage(db.Model):
    __table__ = db.Model.metadata.tables['LightingPackage']
    __table_args__ = dict(autoload=True)

    id = __table__.c.pk_lighting_package_id
    device = __table__.c.ix_device_sn
    timestamp = __table__.c.ix_data_dtm
    mode = __table__.c.ix_mode_ind

# ----------------------------------------------------------------------------------------------------------------------


class MouseGesturePackage(db.Model):
    __table__ = db.Model.metadata.tables['MouseGesturePackage']
    __table_args__ = dict(autoload=True)

    id = __table__.c.pk_mouse_gesture_package_id
    device = __table__.c.ix_device_sn
    timestamp = __table__.c.ix_data_dtm
    gesture_start = __table__.c.gesture_start_dtm
    gesture_end = __table__.c.gesture_end_dtm
    event_count = __table__.c.event_count_int
    gesture_distance = __table__.c.gesture_distance_dbl
    gesture_speed = __table__.c.gesture_speed_dbl
    gesture_deviation = __table__.c.gesture_deviation_dbl

# ----------------------------------------------------------------------------------------------------------------------


class TemperaturePackage(db.Model):
    __table__ = db.Model.metadata.tables['TemperaturePackage']
    __table_args__ = dict(autoload=True)

    id = __table__.c.pk_temperature_package_id
    device = __table__.c.ix_device_sn
    timestamp = __table__.c.ix_data_dtm
    temperature = __table__.c.temperature_dbl
    unit = __table__.c.unit_sn

# ----------------------------------------------------------------------------------------------------------------------


class HumidityPackage(db.Model):
    __table__ = db.Model.metadata.tables['HumidityPackage']
    __table_args__ = dict(autoload=True)

    id = __table__.c.pk_humidity_package_id
    device = __table__.c.ix_device_sn
    timestamp = __table__.c.ix_data_dtm
    humidity = __table__.c.humidity_dbl
    unit = __table__.c.unit_sn


# ----------------------------------------------------------------------------------------------------------------------


class PressurePackage(db.Model):
    __table__ = db.Model.metadata.tables['PressurePackage']
    __table_args__ = dict(autoload=True)

    id = __table__.c.pk_pressure_package_id
    device = __table__.c.ix_device_sn
    timestamp = __table__.c.ix_data_dtm
    pressure = __table__.c.pressure_dbl
    unit = __table__.c.unit_sn


# ----------------------------------------------------------------------------------------------------------------------


class GasPackage(db.Model):
    __table__ = db.Model.metadata.tables['GasPackage']
    __table_args__ = dict(autoload=True)

    id = __table__.c.pk_gas_package_id
    device = __table__.c.ix_device_sn
    timestamp = __table__.c.ix_data_dtm
    gas = __table__.c.gas_ind
    amount = __table__.c.amount_dbl
    unit = __table__.c.unit_sn

# ----------------------------------------------------------------------------------------------------------------------


class BrightnessPackage(db.Model):
    __table__ = db.Model.metadata.tables['BrightnessPackage']
    __table_args__ = dict(autoload=True)

    id = __table__.c.pk_brightness_package
    device = __table__.c.ix_device_sn
    timestamp = __table__.c.ix_data_dtm
    brightness = __table__.c.brightness_int
    source = __table__.c.ix_source_sn
    unit = __table__.c.unit_sn

# ----------------------------------------------------------------------------------------------------------------------


class LoudnessPackage(db.Model):
    __table__ = db.Model.metadata.tables['LoudnessPackage']
    __table_args__ = dict(autoload=True)

    id = __table__.c.pk_loudness_package_id
    device = __table__.c.ix_device_sn
    timestamp = __table__.c.ix_data_dtm
    loudness = __table__.c.loudness_dbl
    unit = __table__.c.unit_sn

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
        last_connection = db.func.max(tp.timestamp).label('last_update')
        return db.session.query(tp.device, last_connection) \
                      .filter(tp.timestamp >= start_date) \
                      .group_by(tp.device)

    # ------------------------------------------------------------------------------------------------------------------

    def query_dashboard(self, start_date):
        """database query for main information dashboard"""
        sq_mode = self.query_mode.subquery()
        sq_mouse = self.query_mouse(start_date).subquery()
        sq_light = self.query_light(start_date).subquery()
        sq_last_connection = self.query_last_connection(start_date).subquery()

        since = db.func.timediff(db.func.now(), sq_mode.c.timestamp).label('since')

        return self.query_info \
                   .outerjoin(sq_mode, DeviceInfo.device == sq_mode.c.device) \
                   .outerjoin(sq_mouse, DeviceInfo.device == sq_mouse.c.device) \
                   .outerjoin(sq_light, DeviceInfo.device == sq_light.c.device) \
                   .outerjoin(sq_last_connection, DeviceInfo.device == sq_last_connection.c.device) \
                   .add_columns(sq_mode.c.mode,
                                since,
                                sq_light.columns.light_count,
                                sq_mouse.c.mouse_count,
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

    def temperature(self, since):
        query_device = self.query_device

        tp = TemperaturePackage
        sq_temperature = db.session.query(tp.device, tp.temperature, tp.unit, tp.timestamp) \
                                .filter(tp.timestamp >= since) \
                                .order_by(tp.device, tp.timestamp) \
                                .subquery()

        data = query_device.outerjoin(sq_temperature, DeviceInfo.device == sq_temperature.c.device) \
                          .add_columns(sq_temperature.c.temperature, sq_temperature.c.unit, sq_temperature.c.timestamp) \
                          .all()

        return _timeseries(data, 'temperature')

    # ------------------------------------------------------------------------------------------------------------------

    def brightness(self, since):
        """ Return timeseries of Brightness package for all devices

        Note:
        -----
        The PTL has 4 different brightness sensors. Which can be distinguied by column BrightnessBackage.source
        """
        sq_device = self.query_device.subquery()

        bp = BrightnessPackage
        data = db.session.query(bp.device, bp.brightness, bp.unit, bp.timestamp, bp.source) \
                      .filter(bp.timestamp >= since) \
                      .outerjoin(sq_device, sq_device.c.device == bp.device) \
                      .order_by(bp.device, bp.timestamp) \
                      .all()

        data = pd.DataFrame(data)
        data = data.set_index(['device', 'source', data.index])
        return data

# ------------------------------------------------------------------------------------------------------------------

    def humidity(self, since):
        sq_device = self.query_device.subquery()

        hp = HumidityPackage
        data = db.session.query(hp.device, hp.humidity, hp.unit, hp.timestamp) \
                      .filter(hp.timestamp >= since) \
                      .outerjoin(sq_device, sq_device.c.device == hp.device) \
                      .order_by(hp.device, hp.timestamp) \
                      .all()

        return _timeseries(data, 'humidity')

# ------------------------------------------------------------------------------------------------------------------

    def pressure(self, since):
        sq_device = self.query_device.subquery()

        pp = PressurePackage
        data = db.session.query(pp.device, pp.pressure, pp.unit, pp.timestamp) \
                      .filter(pp.timestamp >= since) \
                      .join(sq_device, sq_device.c.device == pp.device) \
                      .order_by(pp.device, pp.timestamp) \
                      .all()

        return _timeseries(data, 'pressure')

# ------------------------------------------------------------------------------------------------------------------

    def gas(self, since):
        sq_device = self.query_device.subquery()

        gp = GasPackage
        data = db.session.query(gp.device, gp.gas, gp.amount, gp.unit, gp.timestamp) \
                      .filter(gp.timestamp >= since) \
                      .outerjoin(sq_device, sq_device.c.device == gp.device) \
                      .order_by(gp.device, gp.timestamp) \
                      .all()

        return _timeseries(data, 'amount')

# ----------------------------------------------------------------------------------------------------------------------


class PresenceDetectorStatistics(object):
    def __init__(self):
        self.query_device = db.session.query(DeviceInfo.device)

    # ------------------------------------------------------------------------------------------------------------------

    def _on_off(self, x):
            return 1 if x == "ON" else 0

    # ------------------------------------------------------------------------------------------------------------------

    def on_off_timeseries(self, since):
        sq_device = self.query_device.subquery()
        ip = InstructionPackage
        sq_on_off = db.session.query(ip.device, ip.service, ip.source, ip.timestamp, ip.instruction, ip.target, ip.value) \
                       .filter(ip.source.contains("Lullaby")) \
                       .filter(ip.instruction == "MODE") \
                       .filter(ip.target == "POWER") \
                       .filter(ip.timestamp >= since) \
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
    def errors(self, device_id=None):
        ep = ErrorPackage
        sq_device = db.session.query(DeviceInfo.device).subquery()

        query = db.session.query(ep.device, ep.service, ep.timestamp, ep.errno, ep.message) \
                       .outerjoin(sq_device, sq_device.c.device == ep.device) \
                       .order_by(ep.device)

        if device_id:
            query = query.filter(ep.device == device_id)

        data = pd.DataFrame(query.all())
        data = data.set_index(['device', data.index])
        return data

    # ------------------------------------------------------------------------------------------------------------------

    def logs(self, device_id=None, since=None, until=None, num_lines=None, log_level="TRACE"):
        lp = LoggerPackage

        sq_device = db.session.query(DeviceInfo.device).subquery()

        query = db.session.query(lp.device, lp.source, lp.timestamp, lp.filename, lp.line_number, lp.log_level, lp.message) \
                       .outerjoin(sq_device, sq_device.c.device == lp.device) \
                       .order_by(lp.device)

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

        if num_lines:
            query = query.order_by(lp.timestamp.desc()) \
                         .slice(1, num_lines)

        data = pd.DataFrame(query.all())

        if num_lines:
            data = data.sort_values(by=['timestamp'])

        data = data.set_index(['device', data.index])
        return data

    # ------------------------------------------------------------------------------------------------------------------

    def version(self, device_id=None):
        vp = VersionPackage

        sq_device = db.session.query(DeviceInfo.device).subquery()

        query = db.session.query(vp.device, vp.timestamp, vp.version_timestamp, vp.branch, vp.commit) \
                       .outerjoin(sq_device, sq_device.c.device == vp.device) \
                       .order_by(vp.device)

        if device_id:
            query = query.filter(vp.device == device_id)

        data = pd.DataFrame(query.all())
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

    def gesture_data(self, since):
        column_names = dict(gesture_distance="distance",
                            gesture_speed="speed",
                            gesture_deviation="deviation")

        mgp = MouseGesturePackage
        sq_mouse = db.session.query(mgp.device, mgp.timestamp, mgp.gesture_start, mgp.gesture_end,
                                 mgp.gesture_distance, mgp.gesture_speed, mgp.gesture_deviation) \
                          .filter(mgp.timestamp >= since) \
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
    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="dd.MM.y HH:mm"
    return babel.dates.format_datetime(value, format)

# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('str')
def _str(input):
        return str(input) if input else ""

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

#@app.teardown_request
#def teardown(exception=None):
#    # teardown database session
#    session.close()

# ----------------------------------------------------------------------------------------------------------------------


@app.context_processor
def utility_processor():
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
                _unit=_unit)

# ----------------------------------------------------------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------------------------------------------------------


@app.route('/')
def index():
    dash = Dashboard()
    start_date = datetime.now() - timedelta(days=1)
    dashboard = dash.dashboard(start_date)
    return render_template('home.html', dashboard=dashboard)

# ----------------------------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)
