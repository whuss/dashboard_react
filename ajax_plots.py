import os
import traceback
from abc import abstractmethod
from datetime import timedelta, date
from typing import Dict

import pandas as pd

from bokeh.embed import components
from bokeh.layouts import column
from flask import render_template, jsonify, url_for

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


class AjaxFieldDownload(AjaxField):
    def __init__(self, name: str):
        super().__init__(name)

    def set_value(self, value):
        if value is not None:
            super().set_value(1)
        else:
            super().set_value(None)

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def final_html(self):
        if self._value is not None:
            return f'<button role="button" class="btn btn-secondary bokeh-plot"' \
                   f' data-ajaxid="{self._id}" data-click="download" data-fieldname="{self.name}">' \
                   f'Download' \
                   f'</button>'
        return ""

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
        self.add_field(AjaxFieldDownload(name='download'))

    # ------------------------------------------------------------------------------------------------------------------

    def fetch_data(self):
        data = self._fetch()
        self.field['download'].set_value(data)
        return data

    # ------------------------------------------------------------------------------------------------------------------

    def render(self):
        print(f"Ajax::render(): plot_name={self._plot_name}, parameters={self._plot_parameters}")
        try:
            data = self.fetch_data()
            if data is None:
                plot = None
            else:
                plot = self._plot(data)
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
    def _fetch(self):
        pass

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

        self._start_date = start_of_day(date(2020, 3, 1))

    # ------------------------------------------------------------------------------------------------------------------

    def _fetch(self):
        device = self.parameters.get('device')
        combined_histogram = Errors().crash_restart_histogram(device, self._start_date)
        if combined_histogram is None or combined_histogram.empty:
            return None

        return combined_histogram

    # ------------------------------------------------------------------------------------------------------------------

    def _plot(self, combined_histogram):
        device = self.parameters.get('device')

        # compute time range
        dates = combined_histogram.reset_index().date
        x_range = self._start_date, date.today()

        # compute range of y_axis
        y_range = 0, max(combined_histogram.drop(columns=['end_of_day']).max())

        histogram_data = combined_histogram.reset_index()

        total_number_of_crashes = int(histogram_data.crash_count.sum())
        total_number_of_restarts = int(histogram_data.restart_count.sum())

        self.field['total_number_of_crashes'].set_value(total_number_of_crashes)
        self.field['total_number_of_restarts'].set_value(total_number_of_restarts)

        return plots.plot_crashes(histogram_data, x_range=x_range, y_range=y_range, device=device)

# ----------------------------------------------------------------------------------------------------------------------


class PlotSceneDurations(AjaxPlot):
    def __init__(self, plot_parameters: dict):
        super().__init__(plot_parameters)
        self._start_date = start_of_day(date(2020, 3, 1))

    # ------------------------------------------------------------------------------------------------------------------

    def _fetch(self):
        device = self.parameters.get('device')
        scene_data = get_scene_durations(device, self._start_date)
        if scene_data is None or scene_data.empty:
            return None

        return scene_data

    # ------------------------------------------------------------------------------------------------------------------

    def _plot(self, scene_data):
        fig1 = plots.plot_scene_duration_percentage(scene_data.copy())
        fig2 = plots.plot_on_duration(scene_data.copy())
        fig3 = plots.plot_sporadic_scenes_duration(scene_data)
        return column([fig1, fig2, fig3])

# ----------------------------------------------------------------------------------------------------------------------


class PlotDatabaseSize(AjaxPlot):
    def _fetch(self):
        data = DatabaseDelay().size()
        if data is None or data.empty:
            return None

        return data

    # ------------------------------------------------------------------------------------------------------------------

    def _plot(self, data):
        return plots.plot_database_size(data)

# ----------------------------------------------------------------------------------------------------------------------


class PlotOnOffCycles(AjaxPlot):
    def __init__(self, plot_parameters: dict):
        super().__init__(plot_parameters)
        self._start_date = start_of_day(date(2020, 3, 1))

    # ------------------------------------------------------------------------------------------------------------------

    def _fetch(self):
        device = self.parameters.get('device')
        data = PresenceDetectorStatistics().on_off_cycle_count(device, self._start_date)
        if data is None or data.empty:
            return None

        return data

    # ------------------------------------------------------------------------------------------------------------------

    def _plot(self, data):
        device_data = data.reset_index()

        x_range = self._start_date - timedelta(days=1), date.today() + timedelta(days=1)

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


class PlotErrors(AjaxPlot):
    def __init__(self, plot_parameters: dict):
        super().__init__(plot_parameters)
        self.add_field(AjaxField(name='total_number_of_errors'))
        self._start_date = start_of_day(date(2020, 3, 1))

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _format_next_day(_date):
        return (_date + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

    # ------------------------------------------------------------------------------------------------------------------

    def _fetch(self):
        device = self.parameters.get('device')
        error_heatmap = Errors().error_heatmap_device(device, self._start_date)

        error_heatmap['location'] = error_heatmap.apply(
            lambda row: f"{os.path.basename(row['filename'])}:{row['line_number']}", axis=1)
        # all errors locations in the dataset
        locations = pd.DataFrame(error_heatmap.location.unique(), columns=['location'])
        # assign a unique color for each error location
        locations['colors'] = plots.color_palette(len(locations.location))
        # locations
        #
        eh = error_heatmap.reset_index()
        errors_by_day = eh.drop(columns=['filename', 'line_number']) \
            .groupby(['date']) \
            .sum() \
            .rename(columns=dict(error_count='errors_by_day'))
        eh = eh.join(errors_by_day, on=['date'])
        eh['error_count_normalized'] = eh.error_count / eh.errors_by_day
        eh = eh.merge(locations, on=['location'])
        eh['date_label'] = eh.date
        eh['end_of_day'] = eh.date.apply(PlotErrors._format_next_day)
        eh = eh.set_index(['date', eh.index]).sort_index()
        error_heatmap = eh

        if error_heatmap is None or error_heatmap.empty:
            self.field['total_number_of_errors'].set_value(0)
            return None

        return error_heatmap

    # ------------------------------------------------------------------------------------------------------------------

    def _plot(self, error_heatmap):
        device = self.parameters.get('device')
        x_range = self._start_date, date.today()

        error_histogram = error_heatmap.groupby(['date']).error_count.sum().reset_index()

        self.field['total_number_of_errors'].set_value(error_histogram.error_count.sum())

        error_histogram['end_of_day'] = error_histogram.date.apply(PlotErrors._format_next_day)

        error_histogram = error_histogram.set_index(['date'])

        # compute range of y_axis
        y_range = 0, max(error_histogram.error_count)

        histogram_data = error_histogram.reset_index()
        fig = plots.plot_errors(histogram_data, x_range=x_range, y_range=y_range, device=device)
        fig_heatmap = plots.plot_error_heatmap(error_heatmap, x_range=x_range, device=device)

        return column([fig, fig_heatmap])

# ----------------------------------------------------------------------------------------------------------------------
