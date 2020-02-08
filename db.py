import sqlalchemy as db
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from dataclasses import dataclass, field
from datetime import datetime, timedelta

_host: str = "83.175.125.85"
_user: str = "infinity"
_password: str = "iGe9kH9j"
_dbname: str = "bbf_inf_rep"

engine = db.create_engine(f'mysql://{_user}:{_password}@{_host}/{_dbname}')

Base = declarative_base()
Base.metadata.bind = engine

connection = engine.connect()
metadata = db.MetaData()
metadata.reflect(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

# ----------------------------------------------------------------------------------------------------------------------
# Load all tables
# ----------------------------------------------------------------------------------------------------------------------

device_info = metadata.tables['DeviceInfo']
lighting_package = metadata.tables['LightingPackage']
brightness_package = metadata.tables['BrightnessPackage']
error_package = metadata.tables['ErrorPackage']
gas_package = metadata.tables['GasPackage']
gaze_zone_package = metadata.tables['GazeZonePackage']
humidity_package = metadata.tables['HumidityPackage']
instruction_package = metadata.tables['InstructionPackage']
keyboard_package = metadata.tables['KeyboardPackage']
loudness_package = metadata.tables['LoudnessPackage']
mouse_click_package = metadata.tables['MouseClickPackage']
mouse_gesture_package = metadata.tables['MouseGesturePackage']
mouse_wheel_package = metadata.tables['MouseWheelPackage']
notification_package = metadata.tables['NotificationPackage']
pressure_package = metadata.tables['PressurePackage']
temperatur_package = metadata.tables['TemperaturePackage']

# ----------------------------------------------------------------------------------------------------------------------


class DeviceInfo(Base):
    __tablename__ = 'DeviceInfo'
    __table_args__ = dict(autoload=True)

    device = db.Column('uk_device_sn', key='device')
    mode = db.Column('device_mode_ind', key='mode')
    last_update = db.Column('last_update_dtm', key='last_update')

# ----------------------------------------------------------------------------------------------------------------------


class LightingPackage(Base):
    __tablename__ = 'LightingPackage'
    __table_args__ = dict(autoload=True)

    id = db.Column('pk_lighting_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('create_dtm', key='timestamp')
    mode = db.Column('ix_mode_ind', key='mode')

# ----------------------------------------------------------------------------------------------------------------------


class MouseGesturePackage(Base):
    __tablename__ = 'MouseGesturePackage'
    __table_args__ = dict(autoload=True)

    id = db.Column('pk_mouse_gesture_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('create_dtm', key='timestamp')

# ----------------------------------------------------------------------------------------------------------------------


class TemperaturePackage(Base):
    __tablename__ = 'TemperaturePackage'
    __table_args__ = dict(autoload=True)

    id = db.Column('pk_temperature_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('create_dtm', key='timestamp')
    temperature = db.Column('temperature_dbl', key='temperature')
    unit = db.Column('unit_sn', key='unit')

# ----------------------------------------------------------------------------------------------------------------------


class HumidityPackage(Base):
    __tablename__ = 'HumidityPackage'
    __table_args__ = dict(autoload=True)

    id = db.Column('pk_humidity_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('create_dtm', key='timestamp')
    humidity = db.Column('humidity_dbl', key='humidity')
    unit = db.Column('unit_sn', key='unit')


# ----------------------------------------------------------------------------------------------------------------------


class PressurePackage(Base):
    __tablename__ = 'PressurePackage'
    __table_args__ = dict(autoload=True)

    id = db.Column('pk_pressure_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('create_dtm', key='timestamp')
    pressure = db.Column('pressure_dbl', key='pressure')
    unit = db.Column('unit_sn', key='unit')


# ----------------------------------------------------------------------------------------------------------------------


class GasPackage(Base):
    __tablename__ = 'GasPackage'
    __table_args__ = dict(autoload=True)

    id = db.Column('pk_gas_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('create_dtm', key='timestamp')
    gas = db.Column('gas_ind', key='gas')
    amount = db.Column('amount_dbl', key='amount')
    unit = db.Column('unit_sn', key='unit')

# ----------------------------------------------------------------------------------------------------------------------


class BrightnessPackage(Base):
    __tablename__ = 'BrightnessPackage'
    __table_args__ = dict(autoload=True)

    id = db.Column('pk_brightness_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('create_dtm', key='timestamp')
    brightness = db.Column('brightness_int', key='brightness')
    unit = db.Column('unit_sn', key='unit')

# ----------------------------------------------------------------------------------------------------------------------


class LoudnessPackage(Base):
    __tablename__ = 'LoudnessPackage'
    __table_args__ = dict(autoload=True)

    id = db.Column('pk_loudness_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('create_dtm', key='timestamp')
    loudness = db.Column('loudness_dbl', key='loudness')
    unit = db.Column('unit_sn', key='unit')

# ----------------------------------------------------------------------------------------------------------------------


class Dashboard(object):
    def __init__(self):
        # ---- Device query ----
        self.query_device = session.query(DeviceInfo.device)

        # ---- Info query ----
        self.query_info = session.query(DeviceInfo.device,
                                        DeviceInfo.mode,
                                        DeviceInfo.last_update)

        # ---- Mode query ----
        lp = LightingPackage
        lastone = db.func.max(lp.id).label('lastone')
        last_light_package = session.query(lp.device, lastone) \
                                    .group_by(lp.device)

        sq = last_light_package.subquery()
        # last know operating mode per PTL-device
        self.query_mode = session.query(lp.device, lp.timestamp, lp.mode) \
                                 .join(sq, sq.columns.lastone == lp.id) \
                                 .group_by(lp.device)

        super().__init__()

    # ------------------------------------------------------------------------------------------------------------------

    def query_light(self, start_date):
        """number of lighting changes since start_date per PTL-device"""
        lp = LightingPackage
        light_count = db.func.count(lp.id).label('light_count')
        return session.query(lp.device, light_count) \
                      .filter(lp.timestamp >= start_date) \
                      .group_by(lp.device)

    # ------------------------------------------------------------------------------------------------------------------

    def query_mouse(self, start_date):
        """number of mouse gestures since start_date per PTL-device"""
        mp = MouseGesturePackage
        mouse_count = db.func.count(mp.id).label('mouse_count')
        return session.query(mp.device, mouse_count) \
                      .filter(mp.timestamp >= start_date) \
                      .group_by(mp.device)

    # ------------------------------------------------------------------------------------------------------------------

    def query_dashboard(self, start_date):
        """database query for main information dashboard"""
        sq_mode = self.query_mode.subquery()
        sq_mouse = self.query_mouse(start_date).subquery()
        sq_light = self.query_light(start_date).subquery()

        since = db.func.timediff(db.func.now(), sq_mode.c.timestamp).label('since')

        return self.query_info \
                   .outerjoin(sq_mode, DeviceInfo.device == sq_mode.c.device) \
                   .outerjoin(sq_mouse, DeviceInfo.device == sq_mouse.c.device) \
                   .outerjoin(sq_light, DeviceInfo.device == sq_light.c.device) \
                   .add_columns(sq_mode.c.mode, sq_mouse.c.mouse_count, sq_light.columns.light_count, since) \
                   .order_by(DeviceInfo.device)
    # ------------------------------------------------------------------------------------------------------------------

    def dashboard(self, start_date):
        query = self.query_dashboard(start_date)
        return query.all()

# ----------------------------------------------------------------------------------------------------------------------


class SensorData(object):
    def __init__(self):
        # ---- Device query ----
        self.query_device = session.query(DeviceInfo.device)

        tp = TemperaturePackage
        self.sq_temperature = session.query(tp.device, db.func.max(tp.timestamp), tp.temperature, tp.unit) \
                                     .group_by(tp.device) \
                                     .subquery()

        hp = HumidityPackage
        self.sq_humidity = session.query(hp.device, db.func.max(hp.timestamp), hp.humidity, hp.unit) \
                                  .group_by(hp.device) \
                                  .subquery()

        pp = PressurePackage
        self.sq_pressure = session.query(pp.device, db.func.max(pp.timestamp), pp.pressure, pp.unit) \
                                  .group_by(pp.device) \
                                  .subquery()

        gp = GasPackage
        self.sq_gas = session.query(gp.device, db.func.max(gp.timestamp), gp.gas, gp.amount, gp.unit) \
                             .group_by(gp.device) \
                             .subquery()

        bp = BrightnessPackage
        self.sq_brightness = session.query(bp.device, db.func.max(bp.timestamp), bp.brightness, bp.unit) \
                                    .group_by(bp.device) \
                                    .subquery()

        lp = LoudnessPackage
        self.sq_loudness = session.query(lp.device, db.func.max(lp.timestamp), lp.loudness, lp.unit) \
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
        tp = TemperaturePackage
        sq_temperature = session.query(tp.device, tp.temperature, tp.unit, tp.timestamp) \
                                .filter(tp.timestamp >= since) \
                                .order_by(tp.temperature) \
                                .subquery()

        data = self.query_device \
                   .outerjoin(sq_temperature, DeviceInfo.device == sq_temperature.c.device) \
                   .add_columns(sq_temperature.c.temperature, sq_temperature.c.unit, sq_temperature.c.timestamp) \
                   .order_by(DeviceInfo.device) \
                   .order_by(sq_temperature.c.timestamp) \
                   .all()

        data = pd.DataFrame(data)
        data = data.set_index(['device', data.index])

        devices = self.query_device.all()
        data_dict = {}
        for device in devices:
            device = device[0]
            df = data.loc[device]
            df = df.sort_values(by=['timestamp'])
            data_dict[device] = df[['timestamp', 'temperature']].dropna()

        return data_dict

    # ------------------------------------------------------------------------------------------------------------------

    def brightness(self, since):
        bp = BrightnessPackage
        sq_brightness = session.query(bp.device, bp.brightness, bp.unit, bp.timestamp) \
                               .filter(bp.timestamp >= since) \
                               .order_by(bp.brightness) \
                               .subquery()

        data = self.query_device \
                   .outerjoin(sq_brightness, DeviceInfo.device == sq_brightness.c.device) \
                   .add_columns(sq_brightness.c.brightness, sq_brightness.c.unit, sq_brightness.c.timestamp) \
                   .order_by(DeviceInfo.device) \
                   .order_by(sq_brightness.c.timestamp) \
                   .all()

        data = pd.DataFrame(data)
        data = data.set_index(['device', data.index])

        devices = self.query_device.all()
        data_dict = {}
        for device in devices:
            device = device[0]
            df = data.loc[device]
            df = df.sort_values(by=['timestamp'])
            data_dict[device] = df[['timestamp', 'brightness']].dropna()

        return data_dict

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
        query_device = session.query(DeviceInfo.device)
        
        lp = LightingPackage
        sq_mode = session.query(lp.device, lp.mode, db.func.count(lp.mode).label('count')) \
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


if __name__ == '__main__':
    start_date = datetime.now() - timedelta(days=7)
    dash = Dashboard()
    data = dash.dashboard(start_date)
    print(data[0].keys())

    sensor_data = SensorData()
    sensor = sensor_data.current_temperature()
    print(sensor)
