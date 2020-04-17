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
    if plot_name == "plot_scene_durations":
        return plot_scene_durations(**kwargs)

    if plot_name == "plot_database_size":
        return plot_database_size(**kwargs)

    print(f"Unknown: plot_name={plot_name}")
    return None

# ----------------------------------------------------------------------------------------------------------------------


def hash_id(value):
    from hashlib import md5
    return "id_" + md5(repr(value).encode()).hexdigest()

# ----------------------------------------------------------------------------------------------------------------------


def prepare_plot(plot_name: str, plot_parameters: dict):
    data = dict(plotname=plot_name,
                parameters=plot_parameters)
    plot_id = hash_id(data)
    data['id'] = plot_id
    return data

# ----------------------------------------------------------------------------------------------------------------------
