import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
from datetime import datetime

_host: str = "83.175.125.85"
_user: str = "infinity"
_password: str = "iGe9kH9j"
_dbname: str = "bbf_inf_rep"

engine = sqla.create_engine(f'mysql://{_user}:{_password}@{_host}/{_dbname}')
connection = engine.connect()
metadata = sqla.MetaData()
metadata.reflect(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

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
mouse_gesture_package = metadata.tabels['MouseGesturePackage']
mouse_wheel_package = metadata.tables['MouseWheelPackage']
notification_package = metadata.tabels['NotificationPackage']
pressure_package = metadata.tables['PressurePackage']
temperatur_package = metadata.tables['TemperaturePackage']

# ----------------------------------------------------------------------------------------------------------------------

class Dashboard(object):
    def __init__(self):
        # ---- Info query ----
        self.query_info = session.query(device_info.columns.uk_device_sn,
                                        device_info.columns.device_mode_ind,
                                        device_info.columns.last_update_dtm)


        # ---- Mode query ----

        lc = lighting_package.columns
        lastone = db.func.max(lc.pk_lighting_package_id).label('lastone')
        last_light_query = session.query(lc.ix_device_sn, lastone)
                                        .group_by(lc.ix_device_sn)

        sq = last_light_query.subquery()
        self.query_mode = session.query(lc.ix_device_sn, lc.ix_data_dtm, lc.ix_mode_ind)
                                 .join(sq, lc.pk_lighting_package_id == sq.columns.lastone)
                                 .group_by(lc.ix_device_sn)

        super.__init()

    # ------------------------------------------------------------------------------------------------------------------

    def light_query(self, start_date):
        lc = lighting_package.columns
        return session.query(lc.ix_device_sn, db.func.count(lc).label('light_count'))
                        .filter(lc.ix_data_dtm >= start_date)
                        .group_by(lc.ix_device_sn)

    # ------------------------------------------------------------------------------------------------------------------

    def mouse_query(self, start_date):
        mc = mouse_gesture_package.columns
        return session.query(mc.ix_device_sn, db.func.count(mc).label('mouse_count'))
                        .filter(mc.ix_data_dtm >= start_date)
                        .group_by(mc.ix_device_sn)

    # ------------------------------------------------------------------------------------------------------------------

    def dashboard_query(self, start_date):
        device_sn_info = device_info.columns.uk_device_sn

        sq_mode = self.query_mode.subquery()
        device_sn_mode = sq_mode.columns.ix_device_sn

        sq_mouse = self.query_mouse(start_date).subquery()
        device_sn_mouse = sq_mouse.columns.ix_device_sn

        sq_light = self.query_light(start_date).subquery()
        device_sn_light = sq_light.columns.ix_device_sn

        since = db.func.timediff(db.func.now(), sq_mode.columns.ix_data_dtm).label('since')

        return self.query_info.join(sq_mode, device_sn_info == device_sn_mode)
                              .add_column(sq_mode.columns.ix_mode_ind)
                              .join(sq_mouse, device_sn_info == device_sn_mouse)
                              .add_column(sq_mouse.columns.mouse_count)
                              .join(sq_light, device_sn_info == device_sn_light)
                              .add_column(sq_light.columns.light_count)
                              .add_column(since)

    # ------------------------------------------------------------------------------------------------------------------

    def dashboard(self, start_date):
        query = self.dashboard_query(start_date)
        return query.all()

#start_date = datetime.strptime('2020-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
