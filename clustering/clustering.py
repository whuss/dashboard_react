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
    data = get_input_data(device, start_date, end_date)
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


def plot_distributions(mouse_data: pd.DataFrame):
    sns.set(style="dark")

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
def input_data_clustering(device: str, start_date: date, end_date: Optional[date] = None):
    def add_column_postfix(df: pd.DataFrame, postfix: str) -> pd.DataFrame:
        columns = df.columns
        mapping = {c: f"{c}_{postfix}" for c in columns}
        return df.rename(columns=mapping)

    # get normalized input data
    data = get_input_data(device, start_date, end_date=end_date, normalized=True)

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
    data_rolling = pd.concat(data_rolling_, axis=1).resample("1Min").ffill()

    # normalize rolling data
    st_rolling = QuantileTransformer(output_distribution="normal")
    st_rolling.fit(data_rolling)
    data_rolling_normalized = pd.DataFrame(st_rolling.transform(data_rolling),
                                           columns=data_rolling.columns,
                                           index=data_rolling.index).fillna(0)

    # perform PCA
    pca = PCA()
    pca.fit(data_rolling_normalized)

    variance = np.cumsum(pca.explained_variance_ratio_)

    # how many dimensions to keep for variance over 0.95
    n_dims = variance[variance <= 0.95].shape[0] + 1

    data_pca = pca.transform(data_rolling_normalized)[:, :n_dims]

    # Cluster the data into 5 clusters
    k_means = KMeans(n_clusters=5)
    clustering = k_means.fit_predict(data_pca)

    data_rolling.loc[:, 'cluster'] = clustering
    return data_rolling[['cluster']]

# ----------------------------------------------------------------------------------------------------------------------


def cluster_histogram(cluster_data: pd.DataFrame) -> pd.DataFrame:
    c = cluster_data.reset_index()
    c.loc[:, 'date'] = c.timestamp.dt.date
    c_histogram = pd.DataFrame(c.groupby(['date', 'cluster']).cluster.count())
    c_histogram = c_histogram.rename(columns=dict(cluster="count")).sort_index()

    new_index = pd.MultiIndex.from_product(c_histogram.index.levels, names=['date', 'cluster'])
    c_histogram = c_histogram.reindex(new_index)

    return c_histogram.fillna(0).astype(int)

# ----------------------------------------------------------------------------------------------------------------------
