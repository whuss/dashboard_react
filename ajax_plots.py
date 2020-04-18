from abc import abstractmethod, ABC
import traceback
import sys
import pandas as pd
from flask import render_template, jsonify
from bokeh.embed import components
from typing import Dict
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
        print(f"AjaxFactory::create_plot: plot_name={plot_name}")
        try:
            ajax_class = globals()[plot_name]
        except KeyError:
            raise TypeError(f"AjaxFactory: {plot_name} does not name a class.")
        if not issubclass(ajax_class, Ajax):
            raise TypeError(f"class {ajax_class} does not inherit from Ajax.")
        return ajax_class(plot_parameters)

# ----------------------------------------------------------------------------------------------------------------------


class AjaxField:
    def __init__(self, name: str):
        self.name = name
        self.initial_value = ""
        self._final_html = ""
        self._value = None
        self._id = None

    # ------------------------------------------------------------------------------------------------------------------

    def set_id(self, id):
        self._id = id

    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.html

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def html(self):
        return f'<div class="bokeh-plot" data-ajaxid="{self._id}" data-fieldname="{self.name}">{self.initial_value}</div>'

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def final_html(self):
        return self._final_html

    # ------------------------------------------------------------------------------------------------------------------

    def set_value(self, value):
        self._value = value
        self._final_html = repr(value)

# ----------------------------------------------------------------------------------------------------------------------


class AjaxFieldPlot(AjaxField):
    def __init__(self, name: str):
        super().__init__(name)
        self.initial_value = "Loading plot ..."

    # ------------------------------------------------------------------------------------------------------------------

    def set_value(self, value):
        self._value = value

        if self._value is None:
            self._final_html=f"no data"

        script, div = components(self._value)
        self._final_html=render_template('bokeh_plot.html', div_plot=div, script_plot=script)

# ----------------------------------------------------------------------------------------------------------------------


class Ajax:
    def __init__(self, plot_parameters: dict):
        self._plot_name = self.__class__.__name__
        self._plot_parameters = plot_parameters
        self._data = dict(plot_name=self._plot_name,
                          parameters=plot_parameters)
        self._plot_id = _hash_id(self._data)
        self._data['id'] = self._plot_id
        self._fields: Dict[str, AjaxField] = dict()

    # ------------------------------------------------------------------------------------------------------------------

    def add_field(self, field: AjaxField):
        field.set_id(self._plot_id)
        self._fields[field.name] = field

    @property
    def field(self):
        return self._fields

    # ------------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def _plot(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def render(self):
        pass

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

    def json_data(self):
        data = dict(id=self.id,
                    fields=[dict(fieldname=fieldname, html=field.final_html) for fieldname, field in self._fields.items()]
                    )
        return jsonify(data)

# ----------------------------------------------------------------------------------------------------------------------


class AjaxPlot(Ajax, ABC):
    def __init__(self, plot_parameters: dict):
        super().__init__(plot_parameters)
        self.add_field(AjaxFieldPlot(name='plot'))

    # ------------------------------------------------------------------------------------------------------------------

    def render(self):
        print(f"Ajax::render(): plot_name={self._plot_name}, parameters={self._plot_parameters}")
        try:
            plot = self._plot()
        except Exception:
            tb = traceback.format_exc()
            print(f"Error in plotting function:\n"
                  f"plot_name={self._plot_name}, "
                  f"parameters={self._plot_parameters}\n{tb}")
            plot = None

        self.field['plot'].set_value(plot)

# ----------------------------------------------------------------------------------------------------------------------


class PlotCrashes(AjaxPlot):
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


class PlotSceneDurations(AjaxPlot):
    def _plot(self):
        device = self.parameters.get('device')
        scene_data = get_cached_data(device, None, "scene_durations")
        if scene_data is None:
            return None

        return plots.plot_scene_durations(scene_data)

# ----------------------------------------------------------------------------------------------------------------------


class PlotDatabaseSize(AjaxPlot):
    def _plot(self):
        data = DatabaseDelay().size()
        if data is None:
            return None

        return plots.plot_database_size(data)

# ----------------------------------------------------------------------------------------------------------------------


class PlotOnOffCycles(AjaxPlot):
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
