import logging
from analytics.keyboard import get_keyboard_data
from analytics.mouse import get_mouse_data_raw

from typing import Optional

from db import db_cached

import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

import pandas as pd
from datetime import date, timedelta

from matplotlib.figure import Figure
from sklearn.preprocessing import PowerTransformer, QuantileTransformer

import seaborn as sns

# ----------------------------------------------------------------------------------------------------------------------


def _get_input_data(device: str, start_date: date, end_date: date) -> pd.DataFrame:
    keyboard_data = get_keyboard_data(device, start_date, end_date)
    mouse_data = get_mouse_data_raw(device, start_date, end_date)
    data = pd.merge(keyboard_data, mouse_data, how='outer', left_index=True, right_index=True)
    if 'gesture_duration' in data.columns:
        data = data.drop(columns=['gesture_duration'])
    return data

# ----------------------------------------------------------------------------------------------------------------------


def _get_normalized_input_data(device: str, start_date: date, end_date: date) -> pd.DataFrame:
    data = _get_input_data(device, start_date, end_date)
    if data.empty:
        return data
    pt = PowerTransformer()
    normalized_data = pt.fit_transform(data)
    normalized_data = pd.DataFrame(normalized_data, columns=data.columns, index=data.index)
    return normalized_data

# ----------------------------------------------------------------------------------------------------------------------


def get_input_data(device: str, start_date: date, end_date: Optional[date] = None, normalized=False) -> pd.DataFrame:
    if end_date is None:
        end_date = date.today() - timedelta(days=1)
    if normalized:
        data = _get_normalized_input_data(device, start_date, end_date)
    else:
        data = _get_input_data(device, start_date, end_date)
    return data

# ----------------------------------------------------------------------------------------------------------------------


@db_cached
def get_input_data_sample(device: str, start_date: date, end_date: Optional[date] = None,
                          normalized=False, sample_size: int = 5000) -> pd.DataFrame:
    data = get_input_data(device, start_date, end_date=end_date, normalized=normalized)
    data_size = len(data)
    if data_size <= sample_size:
        return data
    else:
        from sklearn.model_selection import train_test_split
        _, data = train_test_split(data, test_size=min(sample_size, data_size), random_state=31415)
        return data

# ----------------------------------------------------------------------------------------------------------------------


def plot_distribution(mouse_data: pd.DataFrame, column: str):
    sns.set(style="white")

    # Set up the matplotlib figure
    fig = Figure(figsize=(3, 3), constrained_layout=True)
    ax = fig.add_subplot(1, 1, 1)
    try:
        sns.distplot(mouse_data[column].dropna(), ax=ax)
    except KeyError:
        ax.set_xlabel(column)
        logging.warning(f"Column: {column} is not in data frame")

    fig.set_constrained_layout_pads(w_pad=2. / 72., h_pad=2. / 72.,
                                    hspace=0.2, wspace=0.2)
    return fig


# ----------------------------------------------------------------------------------------------------------------------


def plot_distributions(mouse_data: pd.DataFrame):
    # sns.set(style="dark")

    # Set up the matplotlib figure
    fig = Figure(figsize=(3 * 3, 6 * 3), constrained_layout=True)
    for i, c in enumerate(mouse_data.columns):
        ax = fig.add_subplot(6, 3, i+1)
        sns.distplot(mouse_data[c].dropna(), ax=ax)

    fig.set_constrained_layout_pads(w_pad=2. / 72., h_pad=2. / 72.,
                                    hspace=0.2, wspace=0.2)
    return fig

# ----------------------------------------------------------------------------------------------------------------------


@db_cached
def input_data_clustering(device: str, start_date: date, end_date: Optional[date] = None,
                          n_clusters=5,
                          return_only_cluster=True,
                          return_pca=False) -> pd.DataFrame:
    def add_column_postfix(df: pd.DataFrame, postfix: str) -> pd.DataFrame:
        columns = df.columns
        mapping = {c: f"{c}_{postfix}" for c in columns}
        return df.rename(columns=mapping)

    # get normalized input data
    data = get_input_data(device, start_date, end_date=end_date, normalized=True)
    if data.empty:
        return data

    # compute statistics over rolling window
    rolling = data.rolling('15Min', min_periods=1, win_type=None)
    data_rolling_ = list()
    data_rolling_.append(add_column_postfix(rolling.count(), "count"))
    data_rolling_.append(add_column_postfix(rolling.sum(), "sum"))
    data_rolling_.append(add_column_postfix(rolling.mean(), "mean"))
    data_rolling_.append(add_column_postfix(rolling.median(), "median"))
    data_rolling_.append(add_column_postfix(rolling.var(), "var"))
    data_rolling_.append(add_column_postfix(rolling.kurt(), "kurt"))
    data_rolling_.append(add_column_postfix(rolling.skew(), "skew"))
    data_rolling = pd.concat(data_rolling_, axis=1)
    data_rolling = data_rolling.loc[~data_rolling.index.duplicated(keep='first')]
    data_rolling = data_rolling.resample("1Min").nearest(limit=1).dropna(how='all')

    from analytics.instruction import get_power
    power_data = get_power(device, start_date)
    power_data_rolling = power_data.rolling('15Min', min_periods=1, win_type=None).mean()
    data_rolling = data_rolling.merge(power_data_rolling, how='left', left_index=True, right_index=True)
    data_rolling = data_rolling[data_rolling.power >= 0.95]
    data_rolling = data_rolling.drop(columns='power')


    # normalize rolling data
    st_rolling = QuantileTransformer(output_distribution="normal")
    st_rolling.fit(data_rolling)
    data_rolling_normalized = pd.DataFrame(st_rolling.transform(data_rolling),
                                           columns=data_rolling.columns,
                                           index=data_rolling.index).fillna(0)

    # We do not have enough data for a clustering
    if len(data_rolling_normalized) < n_clusters:
        return pd.DataFrame()

    # perform PCA
    pca = PCA(random_state=31415)
    pca.fit(data_rolling_normalized)

    variance = np.cumsum(pca.explained_variance_ratio_)

    # how many dimensions to keep for variance over 0.95
    n_dims = variance[variance <= 0.95].shape[0] + 1

    data_pca = pca.transform(data_rolling_normalized)[:, :n_dims]

    # Cluster the data into 5 clusters
    k_means = KMeans(n_clusters=n_clusters, random_state=31415)
    clustering = k_means.fit_predict(data_pca)

    if return_pca:
        cluster_df = pd.DataFrame(clustering, columns=['cluster'])
        pca_df = pd.DataFrame(data_pca)
        pca_df.columns = [f"d_{c}" for c in pca_df.columns]
        return pd.concat([cluster_df, pca_df], axis=1)

    data_rolling.loc[:, 'cluster'] = clustering
    if return_only_cluster:
        return data_rolling[['cluster']]
    return data_rolling

# ----------------------------------------------------------------------------------------------------------------------


def cluster_histogram(cluster_data: pd.DataFrame):
    c = cluster_data.reset_index()
    c.loc[:, 'date'] = c.timestamp.dt.date
    c_histogram = pd.DataFrame(c.groupby(['date', 'cluster']).cluster.count())
    c_histogram = c_histogram.rename(columns=dict(cluster="count")).sort_index()

    new_index = pd.MultiIndex.from_product(c_histogram.index.levels, names=['date', 'cluster'])
    c_histogram = c_histogram.reindex(new_index)

    return c_histogram.fillna(0).astype(int)

# ----------------------------------------------------------------------------------------------------------------------


def cluster_scatter_matrix(pca_data: pd.DataFrame):
    #sns.set(style='white')
    fig = sns.pairplot(pca_data, hue="cluster", diag_kind="kde", corner=True).fig
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def cluster_palette(num_clusters):
    cp = sns.color_palette('bright')
    return cp[0:num_clusters]

# ----------------------------------------------------------------------------------------------------------------------


def cluster_scatter(pca_data: pd.DataFrame, x_axis: str, y_axis: str):
    num_clusters = len(pca_data.cluster.unique())
    palette = cluster_palette(num_clusters)
    fig = Figure(figsize=(3, 3))
    ax = fig.add_subplot(1, 1, 1)
    if x_axis != y_axis:
        sns.scatterplot(x=x_axis, y=y_axis, data=pca_data, hue='cluster', palette=palette, legend=False, ax=ax)
        ax.set_ylabel('')
        ax.set_xlabel('')
    else:
        for cluster in sorted(pca_data.cluster.unique()):
            sns.kdeplot(pca_data[x_axis][pca_data.cluster == cluster],
                        shade=True, color=palette[cluster], legend=False, ax=ax)

    # Hide axis ticks since the units are meaningless in our case
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def plot_daily_histogram(data, **kwargs):
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
    from datetime import date
    x_range = kwargs.get('x_range', None)
    if not x_range:
        x_range = (date(2020, 2, 1) - timedelta(days=1), date.today() + timedelta(days=1))

    data_t = data.transpose()
    data_t = data_t.rename(columns={date: str(date) for date in data_t.columns})
    data_t = data_t.fillna(0.0)

    num_clusters = len(data_t)

    def color_to_hex(c):
        r, g, b = c
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)
        return f"#{r:02x}{g:02x}{b:02x}"

    palette = cluster_palette(num_clusters)

    data_t['colors'] = [color_to_hex(c) for c in palette]

    data_source = ColumnDataSource(data_t)

    fig = figure(plot_height=200, plot_width=1000,
                 title=f"Daily cluster percentage",
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

    fig.output_backend = "webgl"
    fig.toolbar.logo = None

    fig.add_tools(SaveTool())
    fig.add_tools(WheelZoomTool(dimensions=Dimensions.width))
    fig.add_tools(PanTool(dimensions=Dimensions.width))
    fig.add_tools(ResetTool())
    return fig

# ----------------------------------------------------------------------------------------------------------------------


def plot_daily_timeline(data, **kwargs):
    import itertools
    from datetime import timedelta, datetime, date
    from bokeh.core.enums import Dimensions, StepMode
    from bokeh.transform import dodge, cumsum
    from bokeh.plotting import figure
    from bokeh.models import ColumnDataSource, OpenURL, TapTool
    from bokeh.models import ResetTool, BoxZoomTool, HoverTool, PanTool, SaveTool
    from bokeh.models import NumeralTickFormatter, PrintfTickFormatter, Circle
    from bokeh.models.ranges import Range1d
    from bokeh import palettes, layouts

    from datetime import date
    x_range = kwargs.get('x_range', None)
    if not x_range:
        x_range = (date(2020, 2, 1) - timedelta(days=1), date.today() + timedelta(days=1))

    y_range = 0, 60 * 24  # Minutes of a day

    data_source = ColumnDataSource(data)

    fig = figure(plot_height=500, plot_width=1000,
                 title=f"Cluster timeline",
                 x_axis_type='datetime',
                 y_axis_type='linear',
                 x_range=x_range,
                 y_range=y_range,
                 tools="")

    fig.rect(y='minutes', x='date', width=timedelta(days=1)/2, height=1, color='color', source=data_source)

    from datetime import time

    def index_to_time(index: int):
        hours = index // 60
        minutes = index % 60
        if index == 60 * 24:
            return time(0, 0)
        return time(hours, minutes)

    minutes = list(range(0, 60 * 24 + 1, 3 * 60))
    fig.yaxis.ticker = minutes
    fig.yaxis.major_label_overrides = {m: str(index_to_time(m)) for m in minutes}

    fig.output_backend = "webgl"
    fig.toolbar.logo = None

    hover_tool = HoverTool(tooltips=[('Date', '@date{%F}')],
                           formatters={'date': 'datetime'},
                           mode='vline')

    fig.add_tools(hover_tool)
    fig.add_tools(SaveTool())
    fig.add_tools(BoxZoomTool())
    fig.add_tools(PanTool())
    fig.add_tools(ResetTool())
    return fig

# ----------------------------------------------------------------------------------------------------------------------
