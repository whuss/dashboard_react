import pandas as pd
import numpy as np

from bokeh.plotting import figure

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