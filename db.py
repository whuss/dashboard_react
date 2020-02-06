import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

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
                   .add_columns(sq_mode.c.mode, sq_mouse.c.mouse_count, sq_light.columns.light_count, since)

    # ------------------------------------------------------------------------------------------------------------------

    def dashboard(self, start_date):
        query = self.query_dashboard(start_date)
        return query.all()

# ----------------------------------------------------------------------------------------------------------------------


class SensorData(object):
    def __init__(self):
        # ---- Device query ----
        self.query_device = session.query(device_info.columns.uk_device_sn)

        tp = temperatur_package.columns
        self.query_temperature = session.query(tp.ix_device_sn,
                                               db.func.max(tp.ix_data_dtm),
                                               tp.temperature_dbl,
                                               tp.unit_sn) \
                                        .group_by(tp.ix_device_sn)

        super().__init__()

    # ------------------------------------------------------------------------------------------------------------------

    def current_temperature(self):
        device_sn_info = device_info.columns.uk_device_sn.label('device_id')

        sq_temperature = self.query_temperature.subquery()
        device_sn = sq_temperature.columns.ix_device_sn

        temperature = sq_temperature.columns.temperature_dbl.label('temperature')
        unit = sq_temperature.columns.unit_sn.label('unit')

        return self.query_device \
                   .outerjoin(sq_temperature, device_sn_info == device_sn) \
                   .add_column(device_sn_info) \
                   .add_column(temperature) \
                   .add_column(unit) \
                   .all()


#start_date = datetime.strptime('2020-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    start_date = datetime.now() - timedelta(days=7)
    dash = Dashboard()
    data = dash.dashboard(start_date)
    print(data[0].keys())

    sensor_data = SensorData()
    sensor = sensor_data.current_temperature()
    print(sensor)
