#! /usr/bin/env python3

import pandas as pd
from datetime import datetime, timedelta
from app import db

from db import TemperaturePackage, HumidityPackage, PressurePackage, GasPackage, BrightnessPackage

# Store sensor data from the database and store it as a CSV file.
# This script is intended to generate a datafile to use with the
# mocked Sensors implementation of https://github.com/ReproLight/Infinity

# ----------------------------------------------------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------------------------------------------------

device = 'PTL_RD_AT_001'
since = datetime.strptime('2020-03-22 00:00:00', '%Y-%m-%d %H:%M:%S')
until = since + timedelta(days=1)
num_rows = 1000
filename = "sensor_data.csv"

# ----------------------------------------------------------------------------------------------------------------------

data_frames = []

print("Download temperature data ...", end=" ", flush=True)
tp = TemperaturePackage
query = db.session.query(tp.temperature) \
    .filter(tp.device == device) \
    .filter(tp.timestamp >= since) \
    .filter(tp.timestamp <= until)
data_frames.append(pd.DataFrame(query.limit(num_rows).all()))
print("finished")

print("Download humidity data ...", end=" ", flush=True)
hp = HumidityPackage
query = db.session.query(hp.humidity) \
    .filter(hp.device == device) \
    .filter(hp.timestamp >= since) \
    .filter(hp.timestamp <= until)
data_frames.append(pd.DataFrame(query.limit(num_rows).all()))
print("finished")

print("Download pressure data ...", end=" ", flush=True)
pp = PressurePackage
query = db.session.query(pp.pressure) \
    .filter(pp.device == device) \
    .filter(pp.timestamp >= since) \
    .filter(pp.timestamp <= until)
data_frames.append(pd.DataFrame(query.limit(num_rows).all()))
print("finished")

print("Download gas data ...", end=" ", flush=True)
gp = GasPackage
query = db.session.query(gp.amount) \
    .filter(gp.device == device) \
    .filter(gp.timestamp >= since) \
    .filter(gp.timestamp <= until)
data_frames.append(pd.DataFrame(query.limit(num_rows).all())
                     .rename(columns=dict(amount="gas")))
print("finished")

brightness_sensors = ["brightness_l_h", "brightness_l_v", "brightness_r_h", "brightness_r_v"]
for brightness in brightness_sensors:
    print(f"Download {brightness} data ...", end=" ", flush=True)
    bp = BrightnessPackage
    query = db.session.query(bp.brightness) \
        .filter(bp.device == device) \
        .filter(bp.source == f'{brightness}@BH1750') \
        .filter(bp.timestamp >= since) \
        .filter(bp.timestamp <= until)
    data_frames.append(pd.DataFrame(query.limit(num_rows).all())
                         .rename(columns=dict(brightness=brightness)))
    print("finished")

sensor_data = pd.concat(data_frames, axis=1)

print(f"Save sensor data to {filename} ...", end=" ", flush=True)
sensor_data.to_csv(filename, index=False)
print("finished")
