import pandas as pd
import numpy as np
from datetime import timedelta
from bokeh.core.enums import Dimensions, StepMode
from bokeh.transform import dodge
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, OpenURL, TapTool
from bokeh.models import WheelZoomTool, ResetTool, BoxZoomTool, HoverTool, PanTool, SaveTool, PrintfTickFormatter
from bokeh.models.formatters import NumeralTickFormatter

from flask import url_for

# ----------------------------------------------------------------------------------------------------------------------

def plot_histogram(data, **kwargs):
    """Plot histogram a sequence of data values

    Parameters:
    -----------
    data: iterable of numeric values

    Optional parameters:
    --------------------

    plot_height: int (default=200)

    plot_width: int (default=200)

    title: str (default='')

    x_axis_label: str (default='')

    y_axis_label: str (default='')

    fill_color: str (default='red')
    line_color: str (default='black')
    """
    hist_arr, hist_edges = np.histogram(data)
    hist_df = pd.DataFrame(dict(hist_arr=hist_arr, left=hist_edges[:-1], right=hist_edges[1:]))

    plot_height = kwargs.pop('plot_height', 200)
    plot_width = kwargs.pop('plot_width', 200)
    title = kwargs.pop('title', '')
    x_axis_label = kwargs.pop('x_axis_label', '')
    y_axis_label = kwargs.pop('y_axis_label', '')
    fill_color = kwargs.pop('fill_color', 'red')
    line_color = kwargs.pop('line_color', 'black')

    fig = figure(plot_height=plot_height, plot_width=plot_width,
                 title=title, x_axis_label=x_axis_label, y_axis_label=y_axis_label)
    fig.toolbar.logo = None
    fig.toolbar_location = None

    fig.quad(bottom=0, top=hist_df.hist_arr, left=hist_df.left, right=hist_df.right,
             fill_color=fill_color, line_color=line_color)
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def plot_duration_histogram(data, time_scale: str='s', **kwargs):
    """Plot histogram a sequence of data values

    Parameters:
    -----------
    data: iterable of numeric values

    time_scale: one of "ms"-> milli seconds
                       "s" -> seconds
                       "m" -> minutes
                       "h" -> hours
                       "d" -> days

    Optional parameters:
    --------------------

    plot_height: int (default=200)

    plot_width: int (default=200)

    title: str (default='')

    x_axis_label: str (default='')

    y_axis_label: str (default='')

    fill_color: str (default='red')
    line_color: str (default='black')
    """
    time_format = dict(ms="milli seconds",
                       s="seconds",
                       m="minutes",
                       h="hours",
                       d="days")

    scaled_data = data.astype(f'timedelta64[{time_scale}]')

    hist_arr, hist_edges = np.histogram(scaled_data)
    hist_df = pd.DataFrame(dict(hist_arr=hist_arr, left=hist_edges[:-1], right=hist_edges[1:]))

    plot_height = kwargs.pop('plot_height', 200)
    plot_width = kwargs.pop('plot_width', 200)
    title = kwargs.pop('title', '')
    x_axis_label = kwargs.pop('x_axis_label', '')
    x_axis_label = f"{x_axis_label} ({time_format[time_scale]})"
    y_axis_label = kwargs.pop('y_axis_label', '')
    fill_color = kwargs.pop('fill_color', 'red')
    line_color = kwargs.pop('line_color', 'black')

    fig = figure(plot_height=plot_height, plot_width=plot_width,
                 title=title, x_axis_label=x_axis_label, y_axis_label=y_axis_label)
    fig.output_backend = "svg"
    fig.toolbar.logo = None
    fig.toolbar_location = None

    fig.xaxis[0].formatter = NumeralTickFormatter(format='0.[0]')
    #PrintfTickFormatter(format="%.2f" + time_scale)
    fig.yaxis[0].formatter = NumeralTickFormatter(format='0,0')

    fig.quad(bottom=0, top=hist_df.hist_arr, left=hist_df.left, right=hist_df.right,
             fill_color=fill_color, line_color=line_color)
    return fig

# ----------------------------------------------------------------------------------------------------------------------

def plot_lost_signal(lost_signal, x_range):
    x = lost_signal.timestamp
    y = lost_signal.signal_delay.astype(f'timedelta64[m]')
    y = np.minimum(y, 10)

    return plot_time_series(x, y, x_range,
                            mode="line",
                            title="Signal interval (m)",
                            title_location="right",
                            line_color="green",
                            toolbar_location=None)

# ----------------------------------------------------------------------------------------------------------------------


def plot_time_series(x, y, x_range, **kwargs):
    """Creates an interactive timeseries plot

    Optional arguments:
    -------------------

    title: str
        Figure title

    title_location: str
        Location of title. One of: "above, "below", "left", "right" (default: "above")

    x_axis_label: str

    y_axis_label: str

    line_color: str
        Color of the time series (default: 'navy')

    mode: "step" or "line
    """
    if len(x) == 0:
        return None

    # set the drawing mode (default: line)
    mode = kwargs.pop("mode", "line")

    figure_kwargs = {}
    if "title" in kwargs:
        figure_kwargs['title'] = kwargs['title']
        figure_kwargs['title_location'] = kwargs.get('title_location', "above")

    figure_kwargs['toolbar_location'] = kwargs.get('toolbar_location', "right")

    fig = figure(plot_width=800, plot_height=180, x_range=x_range, x_axis_type='datetime', **figure_kwargs)
    fig.output_backend = "webgl"
    if "title" in kwargs:
        #fig.title.text_font_style = "italic"
        fig.title.offset = 20
    if "x_axis_label" in kwargs:
        fig.xaxis.axis_label = kwargs.pop("x_axis_label")
    if "y_axis_label" in kwargs:
        fig.yaxis.axis_label = kwargs.pop("y_axis_label")
    fig.toolbar.logo = None
    fig.tools = [WheelZoomTool(dimensions=Dimensions.width),
                 PanTool(dimensions=Dimensions.width),
                 ResetTool(),
                 SaveTool(),
                 # TODO: add hover tool
                 # HoverTool(mode='vline')
    ]
    # fig.sizing_mode = 'scale_width'
    line_kwargs = dict()
    line_kwargs['line_color'] = kwargs.get('line_color', 'navy')

    if mode == "step":
        fig.step(
            x=x,
            line_width=1,
            y=y,
            mode=StepMode.after,
            **line_kwargs
        )
    else:
        fig.line(
            x=x,
            line_width=1,
            y=y,
            **line_kwargs
        )

    # render template
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def plot_on_off_cycles(data, **kwargs):
    dates = list(data.date)
    if 'x_range' in kwargs:
        x_range = kwargs['x_range']
    else:
        x_range = (min(dates) - timedelta(days=1), max(dates) + timedelta(days=1))

    night_source = ColumnDataSource(data=data[data['night'] == True])
    day_source = ColumnDataSource(data=data[data['night'] == False])

    vbar_width = timedelta(days=1) / 2.5
    vbar_shift = vbar_width.total_seconds() * 1000

    fig = figure(x_axis_type="datetime", x_range=x_range, plot_height=400, plot_width=1000,
                 title="On/Off Cycles", tools="")
    fig.output_backend = "svg"
    fig.toolbar.logo = None
    fig.add_tools(HoverTool(
        tooltips=[
            ('date', '@date{%F}'),
            ('night', '@night'),
            ('on/off cycles', '@count{%d}')
        ],
        formatters={
            'date': 'datetime',
            'count': 'printf'
        },

        mode='vline'))
    fig.add_tools(SaveTool())

    fig.vbar(x=dodge('date', -vbar_shift / 2, range=fig.x_range),
             width=vbar_width, top='count', source=night_source,
             legend_label='night', line_color="black")
    fig.vbar(x=dodge('date', vbar_shift / 2, range=fig.x_range),
             width=vbar_width, top='count', source=day_source,
             legend_label='day (6:00am - 10:00pm)', color="#fa9fb5", line_color="black")
    fig.legend.location = "top_left"
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def plot_crashes(data, device="PTL_DEFAULT", **kwargs):
    dates = list(data.date)
    if 'x_range' in kwargs:
        x_range = kwargs['x_range']
        x_range = x_range[0] - timedelta(days=1), x_range[1] + timedelta(days=1)
    else:
        x_range = (min(dates) - timedelta(days=1), max(dates) + timedelta(days=1))

    y_range = kwargs.get('y_range', None)

    data_source = ColumnDataSource(data)

    vbar_width = timedelta(days=1) / 2.5
    vbar_shift = vbar_width.total_seconds() * 1000

    fig = figure(x_axis_type="datetime", x_range=x_range, y_range=y_range, plot_height=200, plot_width=800,
                 title="Crashes/Restarts per day", tools="tap")
    fig.output_backend = "svg"
    fig.toolbar.logo = None

    crash_hover_tool = HoverTool(names=['crashes'],
                                 tooltips=[('date', '@date{%F}'),
                                           ('crashes', '@crash_count{%d}')],
                                 formatters={'date': 'datetime',
                                             'crash_count': 'printf'},
                                 mode='vline')

    restart_hover_tool = HoverTool(names=['restarts'],
                                   tooltips=[('date', '@date{%F}'),
                                             ('restarts', '@restart_count{%d}')],
                                   formatters={'date': 'datetime',
                                               'restart_count': 'printf'},
                                   mode='vline')

    fig.add_tools(crash_hover_tool)
    fig.add_tools(restart_hover_tool)
    fig.add_tools(SaveTool())

    fig.vbar(x=dodge('date', -vbar_shift / 2, range=fig.x_range),
             width=vbar_width,
             top='restart_count',
             color='#478c06',
             source=data_source,
             name="restarts",
             legend_label="restarts")
    fig.vbar(x=dodge('date', +vbar_shift / 2, range=fig.x_range),
             width=vbar_width,
             top='crash_count',
             color="#ff3d06",
             source=data_source,
             name="crashes",
             legend_label="crashes")
    fig.legend.location = "top_left"

    url = url_for("show_logs", device=device, timestamp="TIMESTAMP", duration=24*60, log_level="CRITICAL")
    url = url.replace("TIMESTAMP", "@end_of_day")
    taptool = fig.select(type=TapTool)[0]
    print(taptool)
    taptool.callback = OpenURL(url=url, same_tab=True)
    return fig

# ----------------------------------------------------------------------------------------------------------------------

def plot_database_size(data):
    x_range = (min(data.date) - timedelta(days=1), max(data.date) + timedelta(days=1))
    data_source = ColumnDataSource(data)

    fig = figure(x_axis_type="datetime", plot_height=300, plot_width=800, x_range=x_range, tools="",
                 y_axis_label="Database Size (MB)")
    fig.output_backend = "svg"
    fig.toolbar.logo = None

    vbar_width = timedelta(days=1) / 2

    hover_tool = HoverTool(tooltips=[('date', '@date{%F}'),
                                     ('data_size', '@data_size_in_mb{%d}MB'),
                                     ('index_size', '@index_size_in_mb{%d}MB'),
                                     ('total_size', '@total_size{%d}MB')],
                           formatters={'date': 'datetime',
                                       'data_size_in_mb': 'printf',
                                       'index_size_in_mb': 'printf',
                                       'total_size': 'printf',
                                      })
    fig.add_tools(hover_tool)
    fig.add_tools(SaveTool())

    fig.vbar(x='date',
             width=vbar_width,
             top='data_size_in_mb',
             color='#8c8c8c',
             source=data_source,
             name="db_size")
    fig.vbar(x='date',
             width=vbar_width,
             bottom='data_size_in_mb',
             top='total_size',
             color='#c8c8c8',
             source=data_source,
             name="db_size")
    return fig

# ----------------------------------------------------------------------------------------------------------------------
