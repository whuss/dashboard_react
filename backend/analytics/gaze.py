from typing import Optional

import pandas as pd

from db import db, GazeZonePackage
from datetime import date, timedelta

from utils.date import start_of_day, end_of_day
from bokeh.core.enums import Dimensions, StepMode
from bokeh.transform import dodge, cumsum
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, OpenURL, TapTool
from bokeh.models import WheelZoomTool, ResetTool, BoxZoomTool, HoverTool, PanTool, SaveTool
from bokeh.models import NumeralTickFormatter, PrintfTickFormatter, Circle
from bokeh.models import Legend, LegendItem
from bokeh.models.ranges import Range1d
from bokeh import palettes, layouts
from analytics.connection import connection_data_per_day
from analytics.instruction import get_power

# ----------------------------------------------------------------------------------------------------------------------


def get_gaze_data_raw(device: str, start_date: date, end_date: Optional[date] = None) -> pd.DataFrame:
    if end_date is None:
        end_date = date.today()

    since = start_of_day(start_date)
    until = end_of_day(end_date)

    gp = GazeZonePackage

    # Find the timestamp of the last gaze package before the selected time interval
    query_last_timestamp = db.session.query(db.func.max(gp.timestamp).label('timestamp')) \
        .filter(gp.device == device) \
        .filter(gp.timestamp < since)

    sq_last_timestamp = query_last_timestamp.subquery()

    # Get the last recorded gaze package before the selected time interval
    query_last_gaze = db.session.query(gp.zone) \
        .filter(gp.device == device) \
        .filter(gp.timestamp == sq_last_timestamp.c.timestamp)

    first_gaze = query_last_gaze.first()

    # Get gaze packages in the selected time interval
    query = db.session.query(gp.timestamp, gp.zone) \
        .filter(gp.device == device) \
        .filter(gp.timestamp >= since) \
        .filter(gp.timestamp <= until) \
        .order_by(gp.timestamp)

    # Create data frame
    if first_gaze:
        data_since = pd.DataFrame({"timestamp": [since],
                                   "zone": first_gaze.zone})
    else:
        data_since = pd.DataFrame()

    data_between = pd.DataFrame(query.all())

    last_gaze_value = data_between.zone.iloc[-1]
    data_until = pd.DataFrame({"timestamp": [until], 'zone': [last_gaze_value]})

    gaze_data = pd.concat([data_since, data_between, data_until], axis=0)
    return gaze_data

# ----------------------------------------------------------------------------------------------------------------------


def get_gaze_timeseries(device: str, start_date: date, end_date: Optional[date] = None) -> pd.DataFrame:
    if end_date is None:
        end_date = date.today()

    data = get_gaze_data_raw(device, start_date, end_date)
    return data \
        .set_index('timestamp') \
        .resample('1S') \
        .ffill() \
        .reset_index()

# ----------------------------------------------------------------------------------------------------------------------


def get_gaze_intervals(device: str, start_date: date, end_date: Optional[date] = None) -> pd.DataFrame:
    if end_date is None:
        end_date = date.today()

    data = get_gaze_timeseries(device, start_date, end_date)
    # Add date column
    data['date'] = data.timestamp.dt.date
    # Mark the first entry of the day
    data['last_entry_of_day'] = data.date != data.date.shift(-1)
    # Mark the last entry of the day
    data['first_entry_of_day'] = data.date != data.date.shift(1)

    # Keep only rows which are the first row of a new gaze zone detection, or are the first or last entry of a day
    data = data[(data.last_entry_of_day == True) |
                (data.first_entry_of_day == True) |
                (data.zone.shift(1) != data.zone)]

    # Add end-time of each interval
    data['end'] = data.timestamp.shift(-1)
    # Compute duration of each interval
    data['duration'] = data.end - data.timestamp

    # Remove all rows that correspond to the last second of each day, since these were only kept to split
    # the intervals for each day.
    data = data[data.last_entry_of_day == False] \
        .rename(columns=dict(timestamp='begin')) \
        .drop(columns=['last_entry_of_day', 'first_entry_of_day'])
    return data

# ----------------------------------------------------------------------------------------------------------------------


def get_daily_gaze_lengths(device: str, start_date: date, end_date: Optional[date] = None) -> pd.DataFrame:
    if end_date is None:
        end_date = date.today()

    data = get_gaze_intervals(device, start_date, end_date)

    daily_sum = pd.DataFrame(data.groupby(['date', 'zone']).duration.sum())
    daily_sum = daily_sum.unstack().loc[:, 'duration'].fillna(pd.Timedelta(seconds=0))

    connection_data = connection_data_per_day(device, start_date, end_date)
    combined_data = daily_sum.join(connection_data.excluded)
    combined_data = combined_data[combined_data.excluded == 0]
    combined_data = combined_data.drop(columns=['excluded'])

    return combined_data

# ----------------------------------------------------------------------------------------------------------------------


def get_gaze_data(device: str, start_date: date, end_date: Optional[date] = None) -> pd.DataFrame:
    if end_date is None:
        end_date = date.today()

    gp = GazeZonePackage

    query = db.session.query(gp.timestamp, gp.zone) \
        .filter(gp.device == device) \
        .filter(gp.timestamp >= start_date) \
        .filter(gp.timestamp <= end_date) \
        .order_by(gp.timestamp)

    data = pd.DataFrame(query.all())

    if data.empty:
        return data

    data.loc[:, 'end'] = data.timestamp.shift(-1)
    data = data.rename(columns=dict(timestamp='begin'))
    data.iloc[-1, 2] = end_of_day(end_date)
    data['duration'] = data.end - data.begin

    return data

# ----------------------------------------------------------------------------------------------------------------------


def get_daily_gaze_data(device: str, start_date: date, end_date: Optional[date] = None) -> pd.DataFrame:
    if end_date is None:
        end_date = date.today()

    data = get_gaze_data(device, start_date, end_date)

    if data.empty:
        return data

    data['date'] = data.begin.dt.date
    daily_data = pd.DataFrame(data.groupby(['date', 'zone']).duration.sum())
    # daily_data.loc[:, 'count'] = data.groupby(['date', 'zone']).duration.count()

    gaze_data = daily_data.unstack().loc[:, 'duration']

    connection_data = connection_data_per_day(device, start_date, end_date)
    combined_data = gaze_data.join(connection_data.excluded)
    combined_data = combined_data[combined_data.excluded == 0]
    combined_data = combined_data.drop(columns=['excluded'])

    daily_total = pd.DataFrame(combined_data.sum(axis=1), columns=['total'])

    # Since the time intervals of NO_DETECTION usually extend past midnight
    # The sum of all column can be bigger then 24 hours. But when a connection
    # interruption occurs the last conn

    # remove days where the total of all detections exceed 30 hours.
    combined_data = combined_data[daily_total.total <= timedelta(hours=30)]

    return combined_data

# ----------------------------------------------------------------------------------------------------------------------


def get_joined_gaze_power(device: str,
                          start_date: date,
                          end_date: Optional[date] = None,
                          resample_rule: str = '1S') -> pd.DataFrame:
    if end_date is None:
        end_date = date.today()

    gaze_data = get_gaze_timeseries(device, start_date, end_date)
    power_data = get_power(device, start_date, end_date)

    data = pd.merge(power_data, gaze_data, left_index=True, right_on="timestamp").set_index('timestamp')

    # change to one hot encoding for gaze zones
    for zone in data.zone.unique():
        data[zone] = (data.zone == zone).astype(int)
    data = data.drop(columns=['zone'])

    # resample data
    data = data.resample(resample_rule).mean()
    return data

# ----------------------------------------------------------------------------------------------------------------------


def plot_daily_stacked_gaze_detection_durations(data: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """data: a pandas dataframe as produced by get_daily_gaze_data"""
    data = data.drop(columns=['NO_DETECT'])

    data.HORIZONTAL = data.HORIZONTAL.apply(lambda x: x.total_seconds()) / 60
    data.VERTICAL = data.VERTICAL.apply(lambda x: x.total_seconds()) / 60
    data.UNDEFINED = data.UNDEFINED.apply(lambda x: x.total_seconds()) / 60

    y_range = 0, \
              max(data[['HORIZONTAL', 'VERTICAL', 'UNDEFINED']].sum(axis=1))
    if y_range[0] == timedelta(0) and y_range[1] == timedelta(0):
        y_range = (0, 1)

    data = data.rename(columns=dict(HORIZONTAL="horizontal",
                                    VERTICAL="vertical",
                                    UNDEFINED="closed eyes"))

    data_t = data.transpose().reset_index()
    data_t = data_t.rename(columns={date: str(date) for date in data_t.columns})
    data_t['colors'] = palettes.Category10[3]

    from datetime import date
    x_range = kwargs.get('x_range', None)
    if not x_range:
        x_range = (date(2020, 2, 1) - timedelta(days=1), date.today() + timedelta(days=1))

    data_source = ColumnDataSource(data_t)

    fig = figure(plot_height=200, plot_width=1000,
                 title=f"Gaze detections",
                 x_axis_type='datetime',
                 x_range=x_range,
                 y_range=y_range,
                 tools="")
    fig.yaxis.axis_label = "Minutes"

    for date in data.index:
        r = fig.vbar(bottom=cumsum(str(date), include_zero=True),
                     top=cumsum(str(date)),
                     x=date,
                     width=timedelta(days=1) / 2,
                     source=data_source,
                     fill_color='colors',
                     line_color='black',
                     line_width=0)

    fig.output_backend = "svg"
    fig.toolbar.logo = None

    hover_tool = HoverTool(tooltips=[('zone', '@index')],
                           formatters={'index': 'printf'})

    fig.add_tools(hover_tool)
    fig.add_tools(SaveTool())
    fig.add_tools(WheelZoomTool(dimensions=Dimensions.width))
    fig.add_tools(PanTool(dimensions=Dimensions.width))
    fig.add_tools(ResetTool())

    # legend = Legend(items=[LegendItem(label=name, renderers=[r], index=i) for i, name in enumerate(data.columns)])
    # fig.add_layout(legend)
    # fig.legend.location = "top_left"
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def plot_daily_relative_gaze_detection_durations(data: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """data: a pandas dataframe as produced by get_daily_gaze_data"""
    data['total'] = data.HORIZONTAL + data.UNDEFINED + data.VERTICAL
    data.HORIZONTAL /= data.total
    data.UNDEFINED /= data.total
    data.VERTICAL /= data.total

    data = data.drop(columns=['NO_DETECT', 'total'])

    data = data.rename(columns=dict(HORIZONTAL="horizontal",
                                    VERTICAL="vertical",
                                    UNDEFINED="closed eyes"))

    data_t = data.transpose().reset_index()
    data_t = data_t.rename(columns={date: str(date) for date in data_t.columns})
    data_t['colors'] = palettes.Category10[3]

    from datetime import date
    x_range = kwargs.get('x_range', None)
    if not x_range:
        x_range = (date(2020, 2, 1) - timedelta(days=1), date.today() + timedelta(days=1))

    data_source = ColumnDataSource(data_t)

    fig = figure(plot_height=200, plot_width=1000,
                 title=f"Gaze detections",
                 x_axis_type='datetime',
                 x_range=x_range,
                 y_range=(0, 1),
                 tools="")
    fig.yaxis.formatter = NumeralTickFormatter(format='0 %')

    for date in data.index:
        r = fig.vbar(bottom=cumsum(str(date), include_zero=True),
                     top=cumsum(str(date)),
                     x=date,
                     width=timedelta(days=1) / 2,
                     source=data_source,
                     fill_color='colors',
                     line_color='black',
                     line_width=0)

    fig.output_backend = "svg"
    fig.toolbar.logo = None

    hover_tool = HoverTool(tooltips=[('zone', '@index')],
                           formatters={'index': 'printf'})

    fig.add_tools(hover_tool)
    fig.add_tools(SaveTool())
    fig.add_tools(WheelZoomTool(dimensions=Dimensions.width))
    fig.add_tools(PanTool(dimensions=Dimensions.width))
    fig.add_tools(ResetTool())

    # legend = Legend(items=[LegendItem(label=name, renderers=[r], index=i) for i, name in enumerate(data.columns)])
    # fig.add_layout(legend)
    # fig.legend.location = "top_left"
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def plot_daily_gaze_detection_durations(data: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """data: a pandas dataframe as produced by get_daily_gaze_data"""
    data = data.drop(columns=['NO_DETECT'])

    data.HORIZONTAL = data.HORIZONTAL.apply(lambda x: x.total_seconds()) / 60
    data.VERTICAL = data.VERTICAL.apply(lambda x: x.total_seconds()) / 60
    data.UNDEFINED = data.UNDEFINED.apply(lambda x: x.total_seconds()) / 60

    data = data.reset_index()

    from datetime import date
    x_range = kwargs.get('x_range', None)
    if not x_range:
        x_range = (date(2020, 2, 1) - timedelta(days=1), date.today() + timedelta(days=1))

    y_range = min(data[['HORIZONTAL', 'VERTICAL', 'UNDEFINED']].min()), \
        max(data[['HORIZONTAL', 'VERTICAL', 'UNDEFINED']].max())
    if y_range[0] == timedelta(0) and y_range[1] == timedelta(0):
        y_range = (0, 1)

    colors = palettes.Category10[3]

    data_source = ColumnDataSource(data)

    vbar_width = timedelta(days=1) / 6
    vbar_shift = vbar_width.total_seconds() * 1000

    fig = figure(plot_height=200, plot_width=1000,
                 title=f"Gaze detection duration",
                 x_axis_type='datetime',
                 x_range=x_range,
                 y_range=y_range,
                 tools="")
    fig.yaxis.axis_label = "Minutes"

    fig.vbar(bottom=0,
             top='HORIZONTAL',
             x=dodge('date', -vbar_shift, range=fig.x_range),
             width=vbar_width,
             source=data_source,
             fill_color=colors[0],
             line_color='black',
             line_width=0,
             legend_label='horizontal')

    fig.vbar(bottom=0,
             top='UNDEFINED',
             x=dodge('date', 0, range=fig.x_range),
             width=vbar_width,
             source=data_source,
             fill_color=colors[1],
             line_color='black',
             line_width=0,
             legend_label="closed eyes")

    fig.vbar(bottom=0,
             top='VERTICAL',
             x=dodge('date', vbar_shift, range=fig.x_range),
             width=vbar_width,
             source=data_source,
             fill_color=colors[2],
             line_color='black',
             line_width=0,
             legend_label="vertical")

    fig.output_backend = "webgl"
    fig.toolbar.logo = None

    hover_tool = HoverTool(tooltips=[('Date', '@date{%F}'),
                                     ('Horizontal duration', '@HORIZONTAL{0.00} minutes'),
                                     ('Vertical duration', '@VERTICAL{0.00} minutes'),
                                     ('Closed eyes duration', '@UNDEFINED{0.00} minutes')],
                           formatters={'date': 'datetime'},
                           mode='vline')

    fig.add_tools(hover_tool)
    fig.add_tools(SaveTool())
    fig.add_tools(WheelZoomTool(dimensions=Dimensions.width))
    fig.add_tools(PanTool(dimensions=Dimensions.width))
    fig.add_tools(ResetTool())
    fig.legend.location = "top_left"
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def plot_gaze_timeline(data, **kwargs):
    import itertools
    from datetime import timedelta, datetime, date
    from bokeh.core.enums import Dimensions, StepMode
    from bokeh.transform import dodge, cumsum
    from bokeh.plotting import figure
    from bokeh.models import ColumnDataSource, OpenURL, TapTool
    from bokeh.models import WheelZoomTool, ResetTool, BoxZoomTool, HoverTool, PanTool, SaveTool
    from bokeh.models import NumeralTickFormatter, PrintfTickFormatter, Circle
    from bokeh.models.ranges import Range1d
    from bokeh import palettes, layouts
    from bokeh.palettes import Magma256

    from datetime import date
    x_range = kwargs.get('x_range', None)
    if not x_range:
        x_range = (date(2020, 2, 1) - timedelta(days=1), date.today() + timedelta(days=1))

    y_range = 0, 60 * 24  # Minutes of a day

    data['color'] = (data.power * 255).astype(int)
    data['color'] = data.color.apply(lambda c: Magma256[c])

    data_source = ColumnDataSource(data)

    fig = figure(plot_height=500, plot_width=1000,
                 title=f"Power timeline",
                 x_axis_type='datetime',
                 y_axis_type='linear',
                 x_range=x_range,
                 y_range=y_range,
                 tools="")

    fig.rect(y='minutes', x='date', width=timedelta(days=1)/2, height=1, color='orange', source=data_source)

    from datetime import time

    def index_to_time(index: int):
        hours = index // 60
        minutes = index % 60
        if index == 60 * 24:
            return time(0, 0)
        return time(hours, minutes)

    minutes = list(range(0, 60 * 24+1, 3 * 60))
    fig.yaxis.ticker = minutes
    fig.yaxis.major_label_overrides = {m: str(index_to_time(m)) for m in minutes}

    fig.output_backend = "webgl"
    fig.toolbar.logo = None

    hover_tool = HoverTool(tooltips=[('Date', '@date{%F}'),
                                     ('power', '@power')],
                           formatters={'date': 'datetime'})

    fig.add_tools(hover_tool)
    fig.add_tools(SaveTool())
    fig.add_tools(BoxZoomTool())
    fig.add_tools(PanTool())
    fig.add_tools(ResetTool())
    return fig

# ----------------------------------------------------------------------------------------------------------------------
