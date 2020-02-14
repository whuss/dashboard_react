import pandas as pd
import numpy as np
from datetime import timedelta

from bokeh.core.enums import Dimensions, StepMode
from bokeh.transform import dodge
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models import WheelZoomTool, ResetTool, BoxZoomTool, HoverTool, PanTool, SaveTool

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


def plot_time_series(x, y, x_range, **kwargs):
    """Creates an interactive timeseries plot

    Optional arguments:
    -------------------

    title: str
        Figure title

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

    fig = figure(plot_width=800, plot_height=180, x_range=x_range, x_axis_type='datetime', toolbar_location="right", **figure_kwargs)
    if "title" in kwargs:
        fig.title.text_font_style="italic"
        fig.title.offset=20
    fig.toolbar.logo = None
    fig.tools = [WheelZoomTool(dimensions=Dimensions.width),
                 PanTool(dimensions=Dimensions.width),
                 ResetTool(),
                 SaveTool()]
    #fig.sizing_mode = 'scale_width'
    line_kwargs = dict()
    line_kwargs['line_color'] = kwargs.get('line_color', 'navy')

    if mode == "step":
        fig.step(
            x=x,
            line_width=1,
            y=y,
            mode=StepMode.before,
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


def plot_on_off_cycles(data):
    dates = list(data.date)
    x_range = (min(dates) - timedelta(days=1), max(dates) + timedelta(days=1))
    night_source = ColumnDataSource(data=data[data['night'] == True])
    day_source = ColumnDataSource(data=data[data['night'] == False])

    vbar_width = timedelta(days=1) / 2.5
    vbar_shift = vbar_width.total_seconds() * 1000

    fig = figure(x_axis_type="datetime", x_range=x_range, plot_height=400, plot_width=1000,
                 title="On/Off Cycles", tools="")

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

    fig.vbar(x=dodge('date', -vbar_shift / 2, range=fig.x_range),
             width=vbar_width, top='count', source=night_source,
             legend_label='night', line_color="black")
    fig.vbar(x=dodge('date', vbar_shift / 2, range=fig.x_range),
             width=vbar_width, top='count', source=day_source,
             legend_label='day', color="#fa9fb5", line_color="black")
    return fig
