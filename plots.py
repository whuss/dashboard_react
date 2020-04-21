import pandas as pd
import numpy as np
import itertools
from datetime import timedelta
from bokeh.core.enums import Dimensions, StepMode
from bokeh.transform import dodge, cumsum
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, OpenURL, TapTool
from bokeh.models import WheelZoomTool, ResetTool, BoxZoomTool, HoverTool, PanTool, SaveTool
from bokeh.models import NumeralTickFormatter, PrintfTickFormatter
from bokeh.models.ranges import Range1d
from bokeh import palettes, layouts

from flask import url_for
import utils.date

# ----------------------------------------------------------------------------------------------------------------------


def color_palette(size):
    # create palette of 52 unique colors
    palette_generator = itertools.cycle(palettes.Category20[20] +
                                        palettes.Set3[12] +
                                        palettes.Category20b[20])
    # if more colors are needed cycle through the palette
    c = [color for color, _ in zip(palette_generator, range(size))]
    return c


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
    elif mode == "marker":
        fig.step(
            x=x,
            line_width=1,
            y=y,
            mode=StepMode.after,
            **line_kwargs
        )
        fig.circle(x=x, y=y, size=5, color="black")
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
    if y_range and y_range[1] >= 1000:
        bottom = 0.1
        y_range = bottom, y_range[1]
        y_axis_type = "log"
    else:
        bottom = 0
        y_axis_type = "linear"

    data_source = ColumnDataSource(data)

    vbar_width = timedelta(days=1) / 2.5
    vbar_shift = vbar_width.total_seconds() * 1000

    fig = figure(x_axis_type="datetime", y_axis_type=y_axis_type,
                 x_range=x_range, y_range=y_range, plot_height=200, plot_width=800,
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
             bottom=bottom,
             color='#478c06',
             source=data_source,
             name="restarts",
             legend_label="restarts")
    fig.vbar(x=dodge('date', +vbar_shift / 2, range=fig.x_range),
             width=vbar_width,
             top='crash_count',
             bottom=bottom,
             color="#ff3d06",
             source=data_source,
             name="crashes",
             legend_label="crashes")
    fig.legend.location = "top_left"

    url = url_for("show_logs", device=device, timestamp="TIMESTAMP", duration=24*60, log_level="CRITICAL")
    url = url.replace("TIMESTAMP", "@end_of_day")
    taptool = fig.select(type=TapTool)[0]
    taptool.callback = OpenURL(url=url, same_tab=True)
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def plot_errors(data, device="PTL_DEFAULT", **kwargs):
    dates = list(data.date)
    if 'x_range' in kwargs:
        x_range = kwargs['x_range']
        x_range = x_range[0] - timedelta(days=1), x_range[1] + timedelta(days=1)
    else:
        x_range = (min(dates) - timedelta(days=1), max(dates) + timedelta(days=1))

    y_range = kwargs.get('y_range', None)

    data_source = ColumnDataSource(data)

    vbar_width = timedelta(days=1) / 2

    fig = figure(x_axis_type="datetime", x_range=x_range,
                 y_axis_type="log", y_range=y_range,
                 plot_height=200, plot_width=800,
                 title="Errors per day", tools="tap")
    fig.output_backend = "svg"
    fig.toolbar.logo = None

    error_hover_tool = HoverTool(names=['errors'],
                                 tooltips=[('date', '@date{%F}'),
                                           ('errors', '@error_count{%d}')],
                                 formatters={'date': 'datetime',
                                             'error_count': 'printf'},
                                 mode='vline')

    fig.add_tools(error_hover_tool)
    fig.add_tools(SaveTool())

    fig.vbar(x='date',
             width=vbar_width,
             bottom=0.01,
             top='error_count',
             color='#c61803',
             source=data_source,
             name="errors")

    url = url_for("show_logs", device=device, timestamp="TIMESTAMP", duration=24*60, log_level="ERROR")
    url = url.replace("TIMESTAMP", "@end_of_day")
    taptool = fig.select(type=TapTool)[0]
    taptool.callback = OpenURL(url=url, same_tab=False)
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def plot_error_heatmap(data, device="PTL_DEFAULT", **kwargs):
    if 'x_range' in kwargs:
        x_range = kwargs['x_range']
        x_range = x_range[0] - timedelta(days=1), x_range[1] + timedelta(days=1)
    else:
        dates = list(data.date)
        x_range = (min(dates) - timedelta(days=1), max(dates) + timedelta(days=1))

    fig = figure(plot_height=200, plot_width=800,
                 title=f"Error heatmap",
                 x_axis_type='datetime',
                 x_range=x_range,
                 y_range=(0, 1),
                 tools="tap")
    fig.output_backend = "svg"
    fig.toolbar.logo = None
    fig.yaxis.formatter = NumeralTickFormatter(format='0 %')

    error_hover_tool = HoverTool(tooltips=[('date', '@date_label{%F}'),
                                           ('location', '@location'),
                                           ('errors', '@error_count{%d}')],
                                 formatters={'date_label': 'datetime',
                                             'location': 'printf',
                                             'error_count': 'printf'})

    fig.add_tools(error_hover_tool)
    fig.add_tools(SaveTool())

    for date in data.index.get_level_values(0).unique():
        data_source = ColumnDataSource(data.loc[date])
        fig.vbar(bottom=cumsum('error_count_normalized', include_zero=True),
                 top=cumsum('error_count_normalized'),
                 x=date, width=timedelta(days=1)/2, source=data_source, fill_color='colors')

    url = url_for("show_logs", device=device, timestamp="TIMESTAMP", duration=24*60, log_level="ERROR",
                  filename='FILENAME',
                  line_number='LINENUMBER')
    url = url.replace("TIMESTAMP", "@end_of_day") \
             .replace("FILENAME", "@filename") \
             .replace("LINENUMBER", "@line_number")
    taptool = fig.select(type=TapTool)[0]
    taptool.callback = OpenURL(url=url, same_tab=False)

    #tooltips="@location: @error_count Errors",
    return fig


# ----------------------------------------------------------------------------------------------------------------------


def plot_database_size(data):
    x_range = (min(data.date) - timedelta(days=1), max(data.date) + timedelta(days=1))
    data.loc[:, 'bottom'] = 0
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
    # fig.vbar(x='date',
    #          width=vbar_width,
    #          bottom='data_size_in_mb',
    #          top='total_size',
    #          color='#c8c8c8',
    #          source=data_source,
    #          name="db_size")

    fig.varea(x='date',
             y1='bottom',
             y2='data_size_in_mb',
             color='#8c8c8c',
             source=data_source,
             name="db_size_a")
    fig.varea(x='date',
             y1='data_size_in_mb',
             y2='total_size',
             color='#c8c8c8',
             source=data_source,
             name="db_size_a")
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def plot_connection_times(device_data, **kwargs):
    title = kwargs.pop('title', None)
    plot_width = kwargs.pop('plot_width', 800)
    plot_height = kwargs.pop('plot_height', 80 if title else 50)

    if 'x_range' in kwargs:
        x_range = kwargs['x_range']
    else:
        x_range = device_data.begin.min(), device_data.end.max()

    device_data.loc[:, 'duration_str'] = device_data.duration.apply(utils.date.format_time_span)

    def connection_status(connected):
        if connected:
            return "connected"
        else:
            return "lost signal"
    device_data.loc[:, 'connection_status'] = device_data.connected.apply(connection_status)

    # double the height of the hbar when the light is on to make short burst more visible
    device_data['height'] = device_data.connected.apply(lambda x: 0.5 * (2 - x))

    data_source = ColumnDataSource(device_data)

    fig = figure(title=title,
                 x_axis_type="datetime",
                 x_range=x_range, y_range=(0, 1),
                 plot_height=plot_height, plot_width=plot_width)
    fig.hbar(y=0.5, left='begin', right='end', height='height', color='color', line_color=None, source=data_source)
    fig.yaxis.visible = False
    fig.toolbar.logo = None
    fig.toolbar_location = None
    # disable grid
    fig.xgrid.grid_line_color = None
    fig.ygrid.grid_line_color = None
    # disable border
    fig.outline_line_color = None

    hover_tool = HoverTool(tooltips=[('begin', '@begin{%F %H:%M:%S}'),
                                     ('end', '@end{%F %H:%M:%S}'),
                                     ('duration', '@duration_str'),
                                     ('status', '@connection_status')],
                           formatters={'begin': 'datetime',
                                       'end': 'datetime',
                                       'duration_str': 'printf',
                                       'connection_status': 'printf'})
    fig.add_tools(hover_tool)
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def plot_on_off_times(device_data, **kwargs):
    colors = ['#eeeeee', '#ff8e00']  # [off, on]
    plot_width = kwargs.pop('plot_width', 800)
    plot_height = kwargs.pop('plot_height', 80)
    title = kwargs.pop('title', None)

    if 'x_range' in kwargs:
        x_range = kwargs['x_range']
        if isinstance(x_range, tuple):
            x_range = Range1d(x_range[0], x_range[1])
    else:
        x_range = Range1d(device_data.begin.min(), device_data.end.max())

    fig = figure(title=title,
                 x_axis_type="datetime",
                 x_range=x_range, y_range=(0, 1),
                 plot_height=plot_height, plot_width=plot_width,
                 toolbar_location="above")
    fig.yaxis.visible = False
    # disable grid
    fig.xgrid.grid_line_color = None
    fig.ygrid.grid_line_color = None
    # disable border
    fig.outline_line_color = None

    fig.toolbar.logo = None
    fig.tools = [WheelZoomTool(dimensions=Dimensions.width),
                 PanTool(dimensions=Dimensions.width),
                 ResetTool(),
                 SaveTool(),
                 # TODO: add hover tool
                 # HoverTool(mode='vline')
    ]

    if device_data.empty:
        fig.hbar(y=0.5, left=x_range.start, right=x_range.end, height=0.5, color=colors[0], line_color=None)
        return fig

    device_data.loc[:, 'duration_str'] = device_data.duration.apply(utils.date.format_time_span)

    def light_status(connected):
        if connected:
            return "on"
        else:
            return "off"
    device_data.loc[:, 'light_status'] = device_data.value.apply(light_status)

    device_data['color'] = device_data.value.apply(lambda x: colors[x])

    # double the height of the hbar when the light is on to make short burst more visible
    device_data['height'] = device_data.value.apply(lambda x: 0.5 * (x + 1))

    data_source = ColumnDataSource(device_data)

    fig.hbar(y=0.5, left='begin', right='end', height='height', color='color', line_color=None, source=data_source)


    hover_tool = HoverTool(tooltips=[('begin', '@begin{%F %H:%M:%S}'),
                                     ('end', '@end{%F %H:%M:%S}'),
                                     ('duration', '@duration_str'),
                                     ('status', '@light_status')],
                           formatters={'begin': 'datetime',
                                       'end': 'datetime',
                                       'duration_str': 'printf',
                                       'light_status': 'printf'})
    fig.add_tools(hover_tool)
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def plot_scene_duration_percentage(data):
    data.loc[:, 'total_time'] = data.sum(axis=1)
    data.AUTO /= data.total_time
    data.TASK_HORI /= data.total_time
    data.TASK_VERT /= data.total_time
    data.LIGHT_SHOWER /= data.total_time

    data = data.drop(columns=['total_time'])

    # add fake data to see something
    # TODO: remove this
    #day = data.index.min()
    #data.loc[day, :] = [0.25, 0.25, 0.25, 0.25]

    data = data.rename(columns=dict(AUTO="automatic",
                                    TASK_HORI="horizontal task",
                                    TASK_VERT="vertical task",
                                    LIGHT_SHOWER="light shower"))

    data_t = data.transpose()
    data_t = data_t.rename(columns={date: str(date) for date in data_t.columns})
    data_t['colors'] = palettes.Category10[4]

    #x_range = (data.index.min() - timedelta(days=1),
    #           data.index.max() + timedelta(days=1))
    from datetime import date
    x_range = (date(2020, 3, 1) - timedelta(days=1), date.today() + timedelta(days=1))

    data_source = ColumnDataSource(data_t)

    fig = figure(plot_height=200, plot_width=1000,
                 title=f"Scenes",
                 x_axis_type='datetime',
                 x_range=x_range,
                 y_range=(0, 1),
                 tools="")
    fig.yaxis.formatter = NumeralTickFormatter(format='0 %')

    for date in data.index:
        fig.vbar(bottom=cumsum(str(date), include_zero=True),
                 top=cumsum(str(date)),
                 x=date,
                 width=timedelta(days=1) / 2,
                 source=data_source,
                 fill_color='colors',
                 line_color='black',
                 line_width=0)

    fig.output_backend = "svg"
    fig.toolbar.logo = None

    hover_tool = HoverTool(tooltips=[('scene', '@index')],
                           formatters={'scene': 'printf'})

    fig.add_tools(hover_tool)
    fig.add_tools(SaveTool())
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def plot_on_duration(data):
    data.loc[:, 'total_time'] = data.sum(axis=1)

    data = data.reset_index().rename(columns=dict(index="date"))
    data = data[['date', 'total_time']]
    data.loc[:, 'total_time_readable'] = data.total_time.apply(lambda x: utils.date.format_time_span(x))
    data.total_time = data.total_time.apply(lambda x: x.total_seconds() / 60 / 60)

    from datetime import date
    x_range = (date(2020, 3, 1) - timedelta(days=1), date.today() + timedelta(days=1))

    data_source = ColumnDataSource(data)

    fig = figure(plot_height=200, plot_width=1000,
                 title=f"Total on time",
                 x_axis_type='datetime',
                 x_range=x_range,
                 y_range=(0, 24),
                 tools="")
    fig.yaxis.axis_label = "Hours"

    fig.vbar(bottom=0,
             top='total_time',
             x='date',
             width=timedelta(days=1) / 2,
             source=data_source,
             fill_color='red',
             line_color='black',
             line_width=0)

    fig.output_backend = "svg"
    fig.toolbar.logo = None

    hover_tool = HoverTool(tooltips=[('Date', '@date{%F}'),
                                     ('On time', '@total_time_readable')],
                           formatters={'total_time_readable': 'printf',
                                       'date': 'datetime'})

    fig.add_tools(hover_tool)
    fig.add_tools(SaveTool())
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def plot_sporadic_scenes_duration(data):
    data = data.reset_index().rename(columns=dict(index="date"))

    data.TASK_HORI = data.TASK_HORI / 1000 / 60
    data.TASK_VERT = data.TASK_VERT / 1000 / 60
    data.LIGHT_SHOWER = data.LIGHT_SHOWER / 1000 / 60

    from datetime import date
    x_range = (date(2020, 3, 1) - timedelta(days=1), date.today() + timedelta(days=1))

    data_source = ColumnDataSource(data)

    fig = figure(plot_height=200, plot_width=1000,
                 title=f"Total special scene durations",
                 x_axis_type='datetime',
                 x_range=x_range,
                 tools="")
    fig.yaxis.axis_label = "Minutes"

    vbar_width = timedelta(days=1) / 5
    vbar_shift = vbar_width.total_seconds() * 1000

    p = palettes.Category10[4]

    fig.vbar(bottom=0,
             top='TASK_VERT',
             x=dodge('date', -vbar_shift, range=fig.x_range),
             width=vbar_width,
             source=data_source,
             fill_color=p[1],
             line_color='black',
             line_width=0)
    fig.vbar(bottom=0,
             top='TASK_HORI',
             x=dodge('date', 0, range=fig.x_range),
             width=vbar_width,
             source=data_source,
             fill_color=p[2],
             line_color='black',
             line_width=0)
    fig.vbar(bottom=0,
             top='LIGHT_SHOWER',
             x=dodge('date', vbar_shift, range=fig.x_range),
             width=vbar_width,
             source=data_source,
             fill_color=p[3],
             line_color='black',
             line_width=0)

    fig.output_backend = "svg"
    fig.toolbar.logo = None

    hover_tool = HoverTool(tooltips=[('Date', '@date{%F}'),
                                     ('Horizontal task', '@TASK_HORI minutes'),
                                     ('Vertical task', '@TASK_VERT minutes'),
                                     ('Light shower', '@LIGHT_SHOWER minutes')],
                           formatters={'date': 'datetime',
                                       'TASK_HORI': 'printf',
                                       'TASK_VERT': 'printf',
                                       'LIGHT_SHOWER': 'printf'})

    fig.add_tools(hover_tool)
    fig.add_tools(SaveTool())
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def test_plot():
    p = figure(plot_width=400, plot_height=400)

    # add a circle renderer with a size, color, and alpha
    p.circle([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], size=20, color="navy", alpha=0.5)
    return p

# ----------------------------------------------------------------------------------------------------------------------
