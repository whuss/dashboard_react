import traceback
from abc import abstractmethod
from datetime import timedelta, date
from typing import Dict

from bokeh.embed import components
from bokeh.layouts import column
from flask import render_template, jsonify

import plots
from analytics.scenes import get_scene_durations
from db import DatabaseDelay, PresenceDetectorStatistics, Errors, Dashboard
from utils.date import start_of_day, format_time_span
from config import Config


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

    def set_id(self, field_id):
        self._id = field_id

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def value(self):
        if self._value is None:
            return ""

        return self._value

    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.html

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def html(self):
        return f'<div class="bokeh-plot" data-ajaxid="{self._id}" data-fieldname="{self.name}">' \
               f'{self.initial_value}' \
               f'</div>'

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def final_html(self):
        return self._final_html

    # ------------------------------------------------------------------------------------------------------------------

    def set_value(self, value):
        print(f"AjaxField.set_value: id={self._id}, name={self.name}, value={value}")
        self._value = value
        if value is None:
            self._final_html = "no data"
            return
        if isinstance(value, str):
            self._final_html = value
        elif isinstance(value, timedelta):
            self._final_html = format_time_span(value)
        else:
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
            self._final_html = f"no data"
        else:
            script, div = components(self._value)
            self._final_html = render_template('bokeh_plot.html', div_plot=div, script_plot=script)

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

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def field(self):
        return self._fields

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
        fields = [dict(fieldname=name, html=field.final_html) for name, field in self._fields.items()]
        data = dict(id=self.id, fields=fields)
        return jsonify(data)

# ----------------------------------------------------------------------------------------------------------------------


class AjaxPlot(Ajax):
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
            if Config.debug:
                raise

        self.field['plot'].set_value(plot)

    # ------------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def _plot(self):
        pass

# ----------------------------------------------------------------------------------------------------------------------


class PlotCrashes(AjaxPlot):
    def __init__(self, plot_parameters: dict):
        super().__init__(plot_parameters)
        self.add_field(AjaxField(name='total_number_of_crashes'))
        self.add_field(AjaxField(name='total_number_of_restarts'))

    # ------------------------------------------------------------------------------------------------------------------

    def _plot(self):
        start_date = start_of_day(date(2020, 3, 1))
        device = self.parameters.get('device')
        combined_histogram = Errors().crash_restart_histogram(device, start_date)
        if combined_histogram is None or combined_histogram.empty:
            return None

        # compute time range
        dates = combined_histogram.reset_index().date
        x_range = start_date, date.today()

        # compute range of y_axis
        y_range = 0.1, max(combined_histogram.drop(columns=['end_of_day']).max())

        histogram_data = combined_histogram.reset_index()

        total_number_of_crashes = int(histogram_data.crash_count.sum())
        total_number_of_restarts = int(histogram_data.restart_count.sum())

        self.field['total_number_of_crashes'].set_value(total_number_of_crashes)
        self.field['total_number_of_restarts'].set_value(total_number_of_restarts)

        return plots.plot_crashes(histogram_data, x_range=x_range, y_range=y_range, device=device)

# ----------------------------------------------------------------------------------------------------------------------


class PlotSceneDurations(AjaxPlot):
    def _plot(self):
        device = self.parameters.get('device')
        start_date = start_of_day(date(2020, 3, 1))
        scene_data = get_scene_durations(device, start_date)
        if scene_data is None or scene_data.empty:
            return None

        fig1 = plots.plot_scene_duration_percentage(scene_data.copy())
        fig2 = plots.plot_on_duration(scene_data.copy())
        fig3 = plots.plot_sporadic_scenes_duration(scene_data)
        return column([fig1, fig2, fig3])

# ----------------------------------------------------------------------------------------------------------------------


class PlotDatabaseSize(AjaxPlot):
    def _plot(self):
        data = DatabaseDelay().size()
        if data is None or data.empty:
            return None

        return plots.plot_database_size(data)

# ----------------------------------------------------------------------------------------------------------------------


class PlotOnOffCycles(AjaxPlot):
    def _plot(self):
        device = self.parameters.get('device')
        start_date = start_of_day(date(2020, 3, 1))
        data = PresenceDetectorStatistics().on_off_cycle_count(device, start_date)
        if data is None or data.empty:
            return None

        device_data = data.reset_index()

        x_range = start_date - timedelta(days=1), date.today() + timedelta(days=1)

        return plots.plot_on_off_cycles(device_data, x_range=x_range)

# ----------------------------------------------------------------------------------------------------------------------


class DashboardInfo(Ajax):
    def __init__(self, plot_parameters: dict):
        super().__init__(plot_parameters)
        self.add_field(AjaxField(name='study_mode'))
        self.add_field(AjaxField(name='offline_duration'))
        self.add_field(AjaxField(name='health_status'))
        self.add_field(AjaxField(name='sick_reason'))

        self.field['study_mode'].initial_value = "Loading ..."

    # ------------------------------------------------------------------------------------------------------------------

    def render(self):
        device = self.parameters.get('device')
        print(f"Ajax::render(): plot_name={self._plot_name}, parameters={self._plot_parameters}")
        try:
            data = Dashboard.info(device)

            study_mode = data['study_mode']

            html = f'<div class ="deviceMode {study_mode}" data-id="{device}" data-mode="{study_mode}">' \
                   f'{study_mode}' \
                   f'</div>'

            self.field['study_mode'].set_value(html)
            self.field['offline_duration'].set_value(data['offline_duration'])
            health_status = data['health_status']
            self.field['health_status'].set_value(f'<i class="fa fa-heartbeat {health_status}"></i>')
            self.field['sick_reason'].set_value(data['sick_reason'])

        except Exception:
            tb = traceback.format_exc()
            print(f"Error in plotting function:\n"
                  f"plot_name={self._plot_name}, "
                  f"parameters={self._plot_parameters}\n{tb}")
            data = None
            if Config.debug:
                raise

# ----------------------------------------------------------------------------------------------------------------------
