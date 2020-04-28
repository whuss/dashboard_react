import logging
import hashlib
import hmac
import os
import pickle
import traceback
from abc import abstractmethod
from base64 import b64encode, b64decode
from datetime import timedelta, date
from typing import Dict

import pandas as pd
from bokeh.embed import components
from bokeh.layouts import column
from flask import render_template, jsonify

import plots
from analytics.connection import connection, connection_timeseries, connection_data_per_day
from analytics.scenes import get_scene_durations
from analytics.sensors import get_sensor_data
from analytics.keyboard import get_keyboard_data
from config import Config
from db import DatabaseDelay, PresenceDetectorStatistics, Errors, Dashboard
from utils.date import start_of_day, end_of_day, format_time_span, date_range
from utils.interval import find_intervals

# ----------------------------------------------------------------------------------------------------------------------


def _hash_id(value):
    return "id_" + hashlib.md5(repr(value).encode()).hexdigest()

# ----------------------------------------------------------------------------------------------------------------------


class AjaxFactory:
    def __init__(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def create_plot(json_data: dict):
        plot_name, plot_parameters = AjaxFactory._decode_json_data(json_data)
        return AjaxFactory._create_plot(plot_name, plot_parameters)

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _create_plot(plot_name: str, plot_parameters: dict):
        logging.info(f"AjaxFactory::create_plot: plot_name={plot_name}")
        try:
            ajax_class = globals()[plot_name]
        except KeyError:
            raise TypeError(f"AjaxFactory: {plot_name} does not name a class.")
        if not issubclass(ajax_class, Ajax):
            raise TypeError(f"class {ajax_class} does not inherit from Ajax.")
        return ajax_class(plot_parameters)

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _decode_json_data(json_data):
        plot_id = json_data.get('id')
        plot_name = json_data.get('plot_name')
        parameters_encoded = json_data.get('parameters')
        digest = json_data.get('digest')

        # check digest
        client_digest = hmac.new(Config.secret, bytes(parameters_encoded, encoding="ascii"), hashlib.sha1).hexdigest()
        if client_digest != digest:
            raise ValueError(f"The pickle has been tempered with: {digest} != {client_digest}")

        parameters_decoded = pickle.loads(b64decode(parameters_encoded))
        logging.debug(f"decode_json_data: {parameters_decoded}")
        return plot_name, parameters_decoded

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
        logging.info(f"AjaxField.set_value: id={self._id}, name={self.name}, value={value}")
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

    def encode_json_data(self):
        encoded_parameters = b64encode(pickle.dumps(self._plot_parameters)).decode('ascii')
        digest = hmac.new(Config.secret, bytes(encoded_parameters, encoding="ascii"), hashlib.sha1).hexdigest()
        return dict(plot_name=self._plot_name, id=self._plot_id, parameters=encoded_parameters, digest=digest)

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
        logging.info(f"Ajax::render(): plot_name={self._plot_name}, parameters={self._plot_parameters}")
        try:
            data = self.fetch_data()
            if data is None:
                plot = None
            else:
                plot = self._plot(data)
        except Exception:
            tb = traceback.format_exc()
            logging.error(f"Error in plotting function:\n"
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

        self._start_date = start_of_day(date(2020, 2, 1))

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
        self._start_date = start_of_day(date(2020, 2, 1))

    # ------------------------------------------------------------------------------------------------------------------

    def _fetch(self):
        device = self.parameters.get('device')
        scene_data = get_scene_durations(device, self._start_date)
        scene_data.loc[:, 'total_time'] = scene_data.sum(axis=1)
        scene_data = scene_data[scene_data.total_time >= timedelta(minutes=30)]

        if scene_data is None or scene_data.empty:
            return None

        return scene_data

    # ------------------------------------------------------------------------------------------------------------------

    def _plot(self, scene_data):
        fig1 = plots.plot_scene_duration_percentage(scene_data.copy())
        fig2 = plots.plot_on_duration(scene_data.copy(), x_range=fig1.x_range)
        fig3 = plots.plot_sporadic_scenes_duration(scene_data, x_range=fig2.x_range)
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
        self._start_date = start_of_day(date(2020, 2, 1))

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
        logging.info(f"Ajax::render(): plot_name={self._plot_name}, parameters={self._plot_parameters}")
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
            logging.error(f"Error in plotting function:\n"
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
        self._start_date = start_of_day(date(2020, 2, 1))

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

        #
        eh = error_heatmap.loc[device].reset_index()
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


class PlotDatabaseDelay(AjaxPlot):
    def __init__(self, plot_parameters: dict):
        super().__init__(plot_parameters)
        self.add_field(AjaxField(name='number_of_packages'))

    # ------------------------------------------------------------------------------------------------------------------

    def _fetch(self):
        start_date = self.parameters.get('start_date')
        end_date = self.parameters.get('end_date')
        device = self.parameters.get('device')
        data = DatabaseDelay().package_delay(start_date, end_date)

        if data.empty:
            return None

        if device in data.index:
            device_data = data.loc[device].dropna()
        else:
            return None

        total_packages = device_data.delay.count()
        self.field['number_of_packages'].set_value(total_packages)
        return device_data

    # ------------------------------------------------------------------------------------------------------------------

    def _plot(self, device_data):
        fig = plots.plot_duration_histogram(device_data.delay, time_scale="s",
                                            x_axis_label="Package delay", 
                                            y_axis_label="Amount",
                                            plot_width=600, plot_height=400)
        return fig

# ----------------------------------------------------------------------------------------------------------------------


class PlotSensors(AjaxPlot):
    def __init__(self, plot_parameters: dict):
        super().__init__(plot_parameters)
        self.start_date = self.parameters.get('start_date')
        self.end_date = self.parameters.get('end_date')
        self.sensors = self.parameters.get('sensors')
        self.device = self.parameters.get('device')
        self.sample_rate = self.parameters.get('sample_rate')

        self.units = dict(temperature="°C",
                humidity="%RH",
                pressure="hPa",
                brightness="lx",
                gas="VOC kOhm")

        # Make sure that the interval ends at least one day in the past.
        self.end_date = min(self.end_date, date.today() - timedelta(days=1))
        self.start_date = min(self.start_date, self.end_date)

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def supported_sample_rates():
        return ['1s', '1Min', '10Min', '30Min', '1h', '2h', '6h', '12h', '1d', '7d']

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def auto_sample_rate(start_date: date, end_date: date) -> str:
        total_seconds = (end_date - start_date).total_seconds()
        # compute the sample_rate such that there is always 1440 samples in the interval
        # (the number of samples in a day when a sample_rate of 1Min is used)
        if total_seconds > 0:
            sample_rate_in_seconds = int(total_seconds / 1440)
            if sample_rate_in_seconds % 60 == 0:
                sample_rate = f"{sample_rate_in_seconds // 60}Min"
            else:
                sample_rate = f"{sample_rate_in_seconds}s"

        else:
            sample_rate = "1Min"
        return sample_rate

    # ------------------------------------------------------------------------------------------------------------------

    def _fetch(self):
        sensor_data = get_sensor_data(self.device, self.start_date, self.end_date)
        if sensor_data.empty:
            return None
        connection_data = connection_timeseries(self.device, self.start_date, self.end_date)
        data = pd.merge(sensor_data, connection_data, left_index=True, right_index=True)

        if "AUTO" in self.sample_rate:
            self.sample_rate = self.auto_sample_rate(self.start_date, self.end_date)

            logging.info(f"Automatic samplerate: {self.sample_rate}")

        data = data.resample(self.sample_rate).mean()

        return data

    # ------------------------------------------------------------------------------------------------------------------

    def _plot_presence(self, x_range):
        sensor_data = PresenceDetectorStatistics().on_off_timeseries(start_of_day(self.start_date),
                                                                     end_of_day(self.end_date),
                                                                     self.device)

        if sensor_data is None:
            return None
        return plots.plot_on_off_times(sensor_data,
                                       x_range=x_range,
                                       plot_width=1000,
                                       title="Presence detection")

    # ------------------------------------------------------------------------------------------------------------------

    def _plot_connection(self, x_range):
        max_delay = timedelta(seconds=90)
        connection_data = connection(self.device, self.start_date, self.end_date, max_delay, cut_intervals=False)

        if connection_data is None:
            return

        return plots.plot_connection_times(connection_data, x_range=x_range, plot_width=1000,
                                           title="Internet connection")

    # ------------------------------------------------------------------------------------------------------------------

    def _plot(self, sensor_data):
        x_range = (start_of_day(self.start_date), end_of_day(self.end_date))

        figures = list()
        for sensor in self.sensors:
            unit = self.units.get(sensor, "")
            if sensor == "brightness":
                sources = ["brightness_lh", "brightness_lv", "brightness_rh", "brightness_rv"]
                # share y-axis for all brightness plots
                y_range = min(sensor_data[sources].min()), max(sensor_data[sources].max())
            else:
                y_range = None
                sources = [sensor]

            for source in sources:
                if source == "presence":
                    fig = self._plot_presence(x_range)
                else:
                    fig = plots.plot_time_series(sensor_data.index,
                                                 sensor_data[source],
                                                 x_range=x_range,
                                                 y_range=y_range,
                                                 y_axis_label=unit,
                                                 mode='line',
                                                 title=source.capitalize())
                if fig is not None:
                    x_range = fig.x_range
                    figures.append(fig)

        connection_fig = self._plot_connection(x_range)
        if connection_fig:
            figures.append(connection_fig)

        return column(figures)

# ----------------------------------------------------------------------------------------------------------------------


class PlotConnection(AjaxPlot):
    def __init__(self, plot_parameters: dict):
        super().__init__(plot_parameters)
        self.add_field(AjaxField(name='excluded_days'))
        self._start_date = date(2020, 2, 1)
        self._end_date = date.today() - timedelta(days=1)
        self.device = self.parameters.get('device')

    # ------------------------------------------------------------------------------------------------------------------

    def _fetch(self):
        connection_data = connection_data_per_day(self.device, self._start_date, self._end_date)
        if connection_data.empty:
            return None

        self.field['excluded_days'].set_value(f"{connection_data.excluded.sum()}&nbsp;days")
        return connection_data

    # ------------------------------------------------------------------------------------------------------------------

    def _plot(self, connection_data):
        fig1 = plots.plot_excluded_days(connection_data)
        fig2 = plots.plot_connection_per_day(connection_data, x_range=fig1.x_range)
        fig3 = plots.plot_datalosses_per_day(connection_data, x_range=fig2.x_range)
        return column([fig1, fig2, fig3])

# ----------------------------------------------------------------------------------------------------------------------


class PlotKeyboard(AjaxPlot):
    def __init__(self, plot_parameters: dict):
        super().__init__(plot_parameters)
        self._start_date = date(2020, 2, 1)
        self._end_date = date.today() - timedelta(days=1)
        self.device = self.parameters.get('device')

    # ------------------------------------------------------------------------------------------------------------------

    def _fetch(self):
        keyboard_data = get_keyboard_data(self.device, self._start_date, self._end_date)
        if keyboard_data.empty:
            return None

        keyboard_data = keyboard_data.reset_index()
        keyboard_data['date'] = keyboard_data.timestamp.dt.date
        keyboard_data = keyboard_data.set_index('timestamp')

        return keyboard_data

    # ------------------------------------------------------------------------------------------------------------------

    def _plot(self, keyboard_data):
        keyboard_data = keyboard_data.resample('1d').sum()
        fig1 = plots.plot_key_presses(keyboard_data.copy())
        fig2 = plots.plot_special_key_presses(keyboard_data.copy(), x_range=fig1.x_range)
        fig3 = plots.plot_special_key_relative_frequency(keyboard_data.copy(), x_range=fig2.x_range)
        return column([fig1, fig2, fig3])

# ----------------------------------------------------------------------------------------------------------------------
