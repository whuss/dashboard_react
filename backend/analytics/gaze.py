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
    data = get_gaze_data(device, start_date, end_date)

    if data.empty:
        return data

    data['date'] = data.begin.dt.date
    daily_data = pd.DataFrame(data.groupby(['date', 'zone']).duration.sum())
    # daily_data.loc[:, 'count'] = data.groupby(['date', 'zone']).duration.count()

    return daily_data.unstack().loc[:, 'duration']

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

    hover_tool = HoverTool(tooltips=[('zone', '@zone')],
                           formatters={'zone': 'printf'})

    fig.add_tools(hover_tool)
    fig.add_tools(SaveTool())
    fig.add_tools(WheelZoomTool(dimensions=Dimensions.width))
    fig.add_tools(PanTool(dimensions=Dimensions.width))
    fig.add_tools(ResetTool())

    legend = Legend(items=[LegendItem(label=name, renderers=[r], index=i) for i, name in enumerate(data.columns)])
    fig.add_layout(legend)
    fig.legend.location = "top_left"
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def plot_daily_gaze_detection_durations(data: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """data: a pandas dataframe as produced by get_daily_gaze_data"""
    data = data.drop(columns=['NO_DETECT'])

    #data.HORIZONTAL = data.HORIZONTAL.apply(lambda dt: dt.microseconds) / 1000 / 60
    #data.VERTICAL = data.VERTICAL.apply(lambda dt: dt.microseconds) / 1000 / 60
    #data.UNDEFINED = data.UNDEFINED.apply(lambda dt: dt.microseconds) / 1000 / 60

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
