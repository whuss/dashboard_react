import sys
from db import get_cached_data, DatabaseDelay
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

# ----------------------------------------------------------------------------------------------------------------------


def hash_id(value):
    from hashlib import md5
    return "id_" + md5(repr(value).encode()).hexdigest()

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
