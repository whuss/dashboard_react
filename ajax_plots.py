from abc import abstractmethod
import traceback
import sys
import pandas as pd
from datetime import datetime, timedelta, date
from db import get_cached_data, DatabaseDelay, PresenceDetectorStatistics, Errors
import plots
from utils.date import start_of_day


# ----------------------------------------------------------------------------------------------------------------------


def _hash_id(value):
    from hashlib import md5
    return "id_" + md5(repr(value).encode()).hexdigest()

# ----------------------------------------------------------------------------------------------------------------------


class AjaxFactory:
    def __init__(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def create_plot(plot_name: str, plot_parameters: dict):
        try:
            ajax_class = globals()[plot_name]
        except KeyError:
            raise TypeError(f"AjaxFactory: {plot_name} does not name a class.")
        if not issubclass(ajax_class, Ajax):
            raise TypeError(f"class {ajax_class} does not inherit from Ajax.")
        return ajax_class(plot_parameters)

# ----------------------------------------------------------------------------------------------------------------------


class Ajax:
    def __init__(self, plot_parameters: dict):
        self._plot_name = self.__class__.__name__
        self._plot_parameters = plot_parameters
        self._data = dict(plot_name=self._plot_name,
                          parameters=plot_parameters)
        self._plot_id = _hash_id(self._data)
        self._data['id'] = self._plot_id

    # ------------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def _plot(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------

    def render(self):
        print(f"Ajax::render(): plot_name={self._plot_name}, parameters={self._plot_parameters}")
        try:
            return self._plot()
        except Exception:
            tb = traceback.format_exc()
            print(f"Error in plotting function:\n"
                  f"plot_name={self._plot_name}, "
                  f"parameters={self._plot_parameters}\n{tb}")
            return None

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def id(self):
        return self._plot_id

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def data(self):
        return self._data

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def parameters(self):
        return self._plot_parameters

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def html(self):
        return f'<div class="bokeh-plot" id="{self.id}">Loading plot ...</div>'

# ----------------------------------------------------------------------------------------------------------------------


class PlotCrashes(Ajax):
    def _plot(self):
        start_date = start_of_day(date(2020, 3, 1))
        device = self.parameters.get('device')
        combined_histogram = Errors().crash_restart_histogram(device, start_date)
        if combined_histogram is None:
            return None

        # compute time range
        dates = combined_histogram.reset_index().date
        x_range = min(dates), max(dates)

        # compute range of y_axis
        y_range = 0.1, max(combined_histogram.drop(columns=['end_of_day']).max())

        histogram_data = combined_histogram.reset_index()
        return plots.plot_crashes(histogram_data, x_range=x_range, y_range=y_range, device=device)

# ----------------------------------------------------------------------------------------------------------------------


class PlotSceneDurations(Ajax):
    def _plot(self):
        device = self.parameters.get('device')
        scene_data = get_cached_data(device, None, "scene_durations")
        if scene_data is None:
            return None

        return plots.plot_scene_durations(scene_data)

# ----------------------------------------------------------------------------------------------------------------------


class PlotDatabaseSize(Ajax):
    def _plot(self):
        data = DatabaseDelay().size()
        if data is None:
            return None

        return plots.plot_database_size(data)

# ----------------------------------------------------------------------------------------------------------------------


class PlotOnOffCycles(Ajax):
    def _plot(self):
        device = self.parameters.get('device')
        start_date = start_of_day(date(2020, 3, 1))
        data = PresenceDetectorStatistics().on_off_cycle_count(device, start_date)
        if data is None:
            return None

        device_data = data.reset_index()

        x_range = start_date - timedelta(days=1), date.today() + timedelta(days=1)

        return plots.plot_on_off_cycles(device_data, x_range=x_range)

# ----------------------------------------------------------------------------------------------------------------------
