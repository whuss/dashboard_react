import os
import re
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_table import Table, Col, LinkCol
import babel

from bokeh.embed import components
from bokeh.layouts import column
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from typing import Tuple

from dataclasses import dataclass
from datetime import datetime, timedelta

import humanfriendly

from plots import plot_histogram, plot_duration_histogram, plot_time_series
from plots import plot_on_off_cycles, plot_lost_signal

# ----------------------------------------------------------------------------------------------------------------------


_host: str = "83.175.125.85"
#_host: str = "localhost"
_user: str = "infinity"
_password: str = "iGe9kH9j"
_dbname: str = "bbf_inf_rep"

_db_url: str = f'mysql://{_user}:{_password}@{_host}/{_dbname}'

# ----------------------------------------------------------------------------------------------------------------------

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = _db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.Model.metadata.reflect(bind=db.engine)

print(db.Model.metadata.tables.keys())

# ----------------------------------------------------------------------------------------------------------------------


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


@app.route('/')
def index():
    devices = DeviceInfo.query.all()
    #db.session.commit()
    return repr(devices)

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)
