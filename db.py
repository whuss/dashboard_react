import sqlalchemy as db
import pandas as pd
import numpy as np
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from dataclasses import dataclass, field
from datetime import datetime, timedelta

_host: str = "83.175.125.85"
#_host: str = "localhost"
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


class ErrorPackage(Base):
    __tablename__ = 'ErrorPackage'
    __table_args__ = dict(autoload=True)

    id = db.Column('pk_error_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    service = db.Column('service_sn', key='service')
    source = db.Column('ix_source_sn', key='source')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    errno = db.Column('number_int', key="errno")
    message = db.Column('message_str', key="message")

# ----------------------------------------------------------------------------------------------------------------------


class DeviceInfo(Base):
    __tablename__ = 'DeviceInfo'
    __table_args__ = dict(autoload=True)

    device = db.Column('uk_device_sn', key='device')
    mode = db.Column('device_mode_ind', key='mode')
    last_update = db.Column('last_update_dtm', key='last_update')

# ----------------------------------------------------------------------------------------------------------------------


class InstructionPackage(Base):
    __tablename__ = 'InstructionPackage'
    __table_args__ = dict(autoload=True)

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


class LightingPackage(Base):
    __tablename__ = 'LightingPackage'
    __table_args__ = dict(autoload=True)

    id = db.Column('pk_lighting_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    mode = db.Column('ix_mode_ind', key='mode')

# ----------------------------------------------------------------------------------------------------------------------


class MouseGesturePackage(Base):
    __tablename__ = 'MouseGesturePackage'
    __table_args__ = dict(autoload=True)

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


class TemperaturePackage(Base):
    __tablename__ = 'TemperaturePackage'
    __table_args__ = dict(autoload=True)

    id = db.Column('pk_temperature_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    temperature = db.Column('temperature_dbl', key='temperature')
    unit = db.Column('unit_sn', key='unit')

# ----------------------------------------------------------------------------------------------------------------------


class HumidityPackage(Base):
    __tablename__ = 'HumidityPackage'
    __table_args__ = dict(autoload=True)

    id = db.Column('pk_humidity_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    humidity = db.Column('humidity_dbl', key='humidity')
    unit = db.Column('unit_sn', key='unit')


# ----------------------------------------------------------------------------------------------------------------------


class PressurePackage(Base):
    __tablename__ = 'PressurePackage'
    __table_args__ = dict(autoload=True)

    id = db.Column('pk_pressure_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    pressure = db.Column('pressure_dbl', key='pressure')
    unit = db.Column('unit_sn', key='unit')


# ----------------------------------------------------------------------------------------------------------------------


class GasPackage(Base):
    __tablename__ = 'GasPackage'
    __table_args__ = dict(autoload=True)

    id = db.Column('pk_gas_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    gas = db.Column('gas_ind', key='gas')
    amount = db.Column('amount_dbl', key='amount')
    unit = db.Column('unit_sn', key='unit')

# ----------------------------------------------------------------------------------------------------------------------


class BrightnessPackage(Base):
    __tablename__ = 'BrightnessPackage'
    __table_args__ = dict(autoload=True)

    id = db.Column('pk_brightness_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
    brightness = db.Column('brightness_int', key='brightness')
    source = db.Column('ix_source_sn', key='source')
    unit = db.Column('unit_sn', key='unit')

# ----------------------------------------------------------------------------------------------------------------------


class LoudnessPackage(Base):
    __tablename__ = 'LoudnessPackage'
    __table_args__ = dict(autoload=True)

    id = db.Column('pk_loudness_package_id', db.Integer, key='id', primary_key=True)
    device = db.Column('ix_device_sn', key='device')
    timestamp = db.Column('ix_data_dtm', key='timestamp')
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
                                 .join(sq, sq.columns.lastone == lp.id)
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
                                    .filter(bp.source == "brightness_l_h@BH1750") \
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
        query_device = self.query_device

        tp = TemperaturePackage
        sq_temperature = session.query(tp.device, tp.temperature, tp.unit, tp.timestamp) \
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
        data = session.query(bp.device, bp.brightness, bp.unit, bp.timestamp, bp.source) \
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
        data = session.query(hp.device, hp.humidity, hp.unit, hp.timestamp) \
                      .filter(hp.timestamp >= since) \
                      .outerjoin(sq_device, sq_device.c.device == hp.device) \
                      .order_by(hp.device, hp.timestamp) \
                      .all()

        return _timeseries(data, 'humidity')

# ------------------------------------------------------------------------------------------------------------------

    def pressure(self, since):
        sq_device = self.query_device.subquery()

        pp = PressurePackage
        data = session.query(pp.device, pp.pressure, pp.unit, pp.timestamp) \
                      .filter(pp.timestamp >= since) \
                      .join(sq_device, sq_device.c.device == pp.device) \
                      .order_by(pp.device, pp.timestamp) \
                      .all()

        return _timeseries(data, 'pressure')

# ------------------------------------------------------------------------------------------------------------------

    def gas(self, since):
        sq_device = self.query_device.subquery()

        gp = GasPackage
        data = session.query(gp.device, gp.gas, gp.amount, gp.unit, gp.timestamp) \
                      .filter(gp.timestamp >= since) \
                      .outerjoin(sq_device, sq_device.c.device == gp.device) \
                      .order_by(gp.device, gp.timestamp) \
                      .all()

        return _timeseries(data, 'amount')

# ----------------------------------------------------------------------------------------------------------------------


class PresenceDetectorStatistics(object):
    def __init__(self):
        self.query_device = session.query(DeviceInfo.device)

    # ------------------------------------------------------------------------------------------------------------------

    def _on_off(self, x):
            return 1 if x == "ON" else 0

    # ------------------------------------------------------------------------------------------------------------------

    def on_off_timeseries(self, since):
        sq_device = self.query_device.subquery()
        ip = InstructionPackage
        sq_on_off = session.query(ip.device, ip.service, ip.source, ip.timestamp, ip.instruction, ip.target, ip.value) \
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
        sq_device = session.query(DeviceInfo.device).subquery()

        query = session.query(ip.device, ip.source, ip.timestamp, ip.instruction, ip.target, ip.value) \
                    .filter(ip.source.contains("Lullaby")) \
                    .filter(ip.instruction == "MODE") \
                    .filter(ip.target == "POWER") \
                    .filter(ip.value == "ON") \
                    .outerjoin(sq_device, sq_device.c.device == ip.device) \
                    .order_by(ip.device)

        def is_night(date):
            time = date.time()
            return time.hour <= 7 or time.hour >= 9

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
    def errors(self):
        ep = ErrorPackage
        sq_device = session.query(DeviceInfo.device).subquery()

        query = session.query(ep.device, ep.service, ep.timestamp, ep.errno, ep.message) \
                       .outerjoin(sq_device, sq_device.c.device == ep.device) \
                       .order_by(ep.device)

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


class MouseData(object):
    def __init__(self):
        # ---- Device query ----
        self.query_device = session.query(DeviceInfo.device)

    # ------------------------------------------------------------------------------------------------------------------

    def gesture_data(self, since):
        column_names = dict(gesture_distance="distance",
                            gesture_speed="speed",
                            gesture_deviation="deviation")

        mgp = MouseGesturePackage
        sq_mouse = session.query(mgp.device, mgp.timestamp, mgp.gesture_start, mgp.gesture_end,
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
        self.query_device = session.query(DeviceInfo.device)

    # ------------------------------------------------------------------------------------------------------------------

    def package_delay(self, start_date, end_date):
        p = ErrorPackage
        query1 = session.query(p.device, p.create_dtm, p.timestamp) \
                        .filter(p.timestamp >= start_date) \
                        .filter(p.timestamp <= end_date)
        p = InstructionPackage
        query2 = session.query(p.device, p.create_dtm, p.timestamp) \
                        .filter(p.timestamp >= start_date) \
                        .filter(p.timestamp <= end_date)
        p = LightingPackage
        query3 = session.query(p.device, p.create_dtm, p.timestamp) \
                        .filter(p.timestamp >= start_date) \
                        .filter(p.timestamp <= end_date)
        p = MouseGesturePackage
        query4 = session.query(p.device, p.create_dtm, p.timestamp) \
                        .filter(p.timestamp >= start_date) \
                        .filter(p.timestamp <= end_date)
        p = TemperaturePackage
        query5 = session.query(p.device, p.create_dtm, p.timestamp) \
                        .filter(p.timestamp >= start_date) \
                        .filter(p.timestamp <= end_date)
        p = HumidityPackage
        query6 = session.query(p.device, p.create_dtm, p.timestamp) \
                        .filter(p.timestamp >= start_date) \
                        .filter(p.timestamp <= end_date)
        p = PressurePackage
        query7 = session.query(p.device, p.create_dtm, p.timestamp) \
                        .filter(p.timestamp >= start_date) \
                        .filter(p.timestamp <= end_date)
        p = GasPackage
        query8 = session.query(p.device, p.create_dtm, p.timestamp) \
                        .filter(p.timestamp >= start_date) \
                        .filter(p.timestamp <= end_date)
        p = BrightnessPackage
        query9 = session.query(p.device, p.create_dtm, p.timestamp) \
                         .filter(p.timestamp >= start_date) \
                         .filter(p.timestamp <= end_date)
        p = LoudnessPackage
        query10 = session.query(p.device, p.create_dtm, p.timestamp) \
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
    data = pd.DataFrame(data)
    data = data.set_index(['device', data.index])

    devices = data.index.levels[0]
    data_dict = {}
    for device in devices:
        df = data.loc[device]
        df = df.sort_values(by=['timestamp'])
        data_dict[device] = df[['timestamp', sensor]].dropna()

    return data_dict

# ----------------------------------------------------------------------------------------------------------------------


def dataframe_from_query(query):
    """Return the result of a SQLAlchemy query as a pandas dataframe"""
    return pd.read_sql(query.statement, query.session.bind)

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    start_date = datetime.now() - timedelta(days=7)
    dash = Dashboard()
    data = dash.dashboard(start_date)
    print(data[0].keys())

    print(InstructionPackage().getColumns())