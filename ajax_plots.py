import sys
from datetime import datetime, timedelta, date
from db import get_cached_data, DatabaseDelay, PresenceDetectorStatistics
import plots

# ----------------------------------------------------------------------------------------------------------------------


def plot_scene_durations(**kwargs):
    scene_data = get_cached_data(kwargs['device'], None, "scene_durations")
    if scene_data is None:
        return None

    return plots.plot_scene_durations(scene_data)

# ----------------------------------------------------------------------------------------------------------------------


def plot_database_size(**kwargs):
    data = DatabaseDelay().size()
    if data is None:
        return None

    return plots.plot_database_size(data)

# ----------------------------------------------------------------------------------------------------------------------


def plot_on_off_cycles(**kwargs):
    device = kwargs['device']
    start_date = date(2020, 3, 1)
    data = PresenceDetectorStatistics().on_off_cycle_count(device, start_date)
    if data is None:
        return None

    device_data = data.reset_index()

    x_range = start_date - timedelta(days=1), date.today() + timedelta(days=1)

    return plots.plot_on_off_cycles(device_data, x_range=x_range)

# ----------------------------------------------------------------------------------------------------------------------


def get_plot_per_name(plot_name: str, **kwargs):
    print(f"get_plot_per_name(): plot_name={plot_name}")
    current_module = sys.modules[__name__]

    try:
        plot_fn = getattr(current_module, plot_name)
        return plot_fn(**kwargs)
    except AttributeError as e:
        print(f"Unknown: plot_name={plot_name}")
        print(e)
        return None
    except Exception as e:
        print(f"Error in plotting function: {str(e)}")
        return None


# ----------------------------------------------------------------------------------------------------------------------


def hash_id(value):
    from hashlib import md5
    return "id_" + md5(repr(value).encode()).hexdigest()

# ----------------------------------------------------------------------------------------------------------------------


class AjaxPlot:
    def __init__(self, plot_name: str, plot_parameters: dict):
        current_module = sys.modules[__name__]
        try:
            plot_fn = getattr(current_module, plot_name)
        except AttributeError as e:
            print(f"Prepare_plot: Unknown: plot_name={plot_name}")

        self._data = dict(plotname=plot_name,
                          parameters=plot_parameters)
        self._plot_id = hash_id(self._data)
        self._data['id'] = self._plot_id

    @property
    def id(self):
        return self._plot_id

    @property
    def data(self):
        return self._data

    @property
    def parameters(self):
        return self._data['parameters']

    @property
    def html(self):
        return f'<div class="bokeh-plot" id="{self.id}">Loading plot ...</div>'

# ----------------------------------------------------------------------------------------------------------------------


def prepare_plot(plot_name: str, plot_parameters: dict):
    current_module = sys.modules[__name__]
    try:
        plot_fn = getattr(current_module, plot_name)
    except AttributeError as e:
        print(f"Prepare_plot: Unknown: plot_name={plot_name}")

    data = dict(plotname=plot_name,
                parameters=plot_parameters)
    plot_id = hash_id(data)
    data['id'] = plot_id
    return data

# ----------------------------------------------------------------------------------------------------------------------
