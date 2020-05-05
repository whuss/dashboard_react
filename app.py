import os
import re
import pandas as pd
import numpy as np
from typing import Optional

from flask import Flask, render_template, jsonify, request, url_for, json
import dateutil.parser

from config import Config

from db import db
from db import Errors, Dashboard, ModeStatistics, MouseData, PresenceDetectorStatistics, SensorData
from db import Connectivity

# from flask_basicauth import BasicAuth
from flask_table import Col, LinkCol, Table
import babel

from bokeh.embed import components
from bokeh.layouts import column
from bokeh.resources import INLINE

from typing import Tuple, Iterable

from datetime import datetime, timedelta, date

import humanfriendly

from plots import plot_histogram, plot_time_series, plot_connection_times, plot_on_off_times

from ajax_plots import AjaxFactory, PlotCrashes, PlotDatabaseSize, PlotOnOffCycles, PlotSceneDurations, DashboardInfo
from ajax_plots import PlotErrors, PlotDatabaseDelay, PlotSensors, PlotConnection, PlotKeyboard, PlotKeypress, PlotMouse
from ajax_plots import PlotClusteringInputDistribution

from utils.excel import convert_to_excel
from base64 import b64encode

import utils.date

from db import get_devices
from logs import fetch_logs

import logging
import coloredlogs
from logging.config import dictConfig


# ----------------------------------------------------------------------------------------------------------------------
# Logging configuration
# ----------------------------------------------------------------------------------------------------------------------

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

coloredlogs.install(level='DEBUG', fmt='[%(asctime)s] %(levelname)s(%(name)s) in %(module)s: %(message)s')

# ----------------------------------------------------------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------------------------------------------------------


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_BINDS'] = dict(cache=Config.db_cache_url)
    # app.config['BASIC_AUTH_USERNAME'] = "ReproLight"
    # app.config['BASIC_AUTH_PASSWORD'] = "infinity"
    # app.config['BASIC_AUTH_FORCE'] = True
    db.init_app(app)

    # basic_auth = BasicAuth(app)
    return app


# ----------------------------------------------------------------------------------------------------------------------


app = create_app()
app.app_context().push()
db.Model.metadata.reflect(bind=db.engine)


# ----------------------------------------------------------------------------------------------------------------------
# Jinja customization
# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('ajax_plots_to_json')
def ajax_plots_to_json(ajax_plots):
    return json.dumps([plot.encode_json_data() for plot in ajax_plots])

# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('datetime')
def format_datetime(value, format='medium'):
    if not value:
        return ""
    if isinstance(value, str):
        value = utils.date.parse_date(value)

    if format == 'full':
        format = "EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format = "y-MM-dd HH:mm"
    return babel.dates.format_datetime(value, format)


# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('str')
def _str(_input):
    return str(_input) if _input else ""


# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('or_else')
def _or_else(_input, else_input):
    return str(_input) if _input else str(else_input)

# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('capitalize')
def capitalize(_input):
    return str(_input).capitalize() if _input else ""


# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('timespan')
def _time_span(_input):
    if _input:
        utils.date.format_time_span(_input)
    return ""


# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('none')
def _number(_input):
    if pd.isna(_input):
        return ""
    return _input if _input else ""


# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('unit')
def _unit(_input, unit='°C'):
    if not _input:
        return ""
    return f"{_input:.2f} {unit}"


# ----------------------------------------------------------------------------------------------------------------------


@app.template_filter('format_duration')
def _format_duration(_input):
    try:
        minutes = int(_input)
        if minutes < 60:
            return f"{minutes} minutes"
        elif minutes % 60 == 0 and minutes // 60 < 24:
            return f"{minutes // 60} hours"
        elif minutes == 60 * 24:
            return f"1 day"
        else:
            return humanfriendly.format_timespan(timedelta(minutes=minutes), max_units=2)
    except ValueError:
        # input is not an integer
        return str(minutes)

# ----------------------------------------------------------------------------------------------------------------------


@app.context_processor
def utility_processor():
    def _str(_input):
        return str(_input) if _input else ""

    # ------------------------------------------------------------------------------------------------------------------

    def _time_span(_input):
        if _input:
            seconds = _input.seconds
            minutes = seconds // 60
            seconds = seconds % 60
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours:02}:{minutes:02}:{seconds:02}"
            # return humanfriendly.format_timespan(input, max_units=2)
        return ""

    # ------------------------------------------------------------------------------------------------------------------

    def _number(_input):
        return _input if _input else ""

    # ------------------------------------------------------------------------------------------------------------------

    def _unit(_input, unit):
        if not _input:
            return ""
        return f"{_input:.2f} {unit}"

    # ------------------------------------------------------------------------------------------------------------------

    return dict(_str=_str,
                _time_span=_time_span,
                _number=_number,
                _unit=_unit)


# ----------------------------------------------------------------------------------------------------------------------<


def url_for_self(**args):
    return url_for(request.endpoint, **dict(request.view_args, **args))


# ----------------------------------------------------------------------------------------------------------------------<


app.jinja_env.globals['url_for_self'] = url_for_self


# ----------------------------------------------------------------------------------------------------------------------<
# Routes
# ----------------------------------------------------------------------------------------------------------------------


@app.route('/')
def index():
    def _info(device):
        return DashboardInfo(plot_parameters={'device': device})

    ajax_plot_list = [_info(device) for device in get_devices()]

    return render_template('home.html', ajax_plot_list=ajax_plot_list)

# ----------------------------------------------------------------------------------------------------------------------


class PreCol(Col):
    """Column class for Flask Table that wraps its content in a pre tag"""

    def td_format(self, content):
        return f'''<pre style="text-align: left; width: 75%; white-space: pre-line;">
                       {content}
                   </pre>'''


# ----------------------------------------------------------------------------------------------------------------------


class CrashCol(Col):
    def td_format(self, content):
        c = 'SICK' if content else 'HEALTHY'
        return f'''<i class="fa fa-heartbeat {c}"></i>'''


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/system/crashes/<device>')
def crash_for_device(device):
    data = Errors().crashes(device=device)
    device_data = data.reset_index()

    device_data['formatted_message'] = device_data.apply(format_logentry, axis=1)

    class CrashTable(Table):
        classes = ["error-table"]
        timestamp = LinkCol('Time', 'show_logs',
                            url_kwargs=dict(device='device', timestamp='timestamp'),
                            url_kwargs_extra=dict(duration=5, log_level='TRACE'),
                            attr='timestamp')
        formatted_message = PreCol('Error message')

    table = CrashTable(device_data.to_dict(orient='records'))

    return render_template("crashes_device.html", device=device, table=table)


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/system/errors')
def error_statistics():
    def _plot(device):
        return PlotErrors(plot_parameters={'device': device})

    ajax_plot_list = [_plot(device) for device in get_devices()]

    return render_template("error_statistics.html",
                           ajax_plot_list=ajax_plot_list,
                           js_resources=INLINE.render_js(),
                           css_resources=INLINE.render_css()
                           )

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/system/error_heatmap')
def error_heatmap():
    data = Errors().error_heatmap()
    data['location'] = data.apply(lambda row: f"{os.path.basename(row['filename'])}:{row['line_number']}", axis=1)

    class HeatmapTable(Table):
        classes = ["error-table"]
        date = LinkCol('Date', 'show_logs',
                       url_kwargs=dict(device='device',
                                       timestamp='end_of_day',
                                       filename='filename',
                                       line_number='line_number'),
                       url_kwargs_extra=dict(log_level='ERROR', duration=60 * 24), attr="date")
        location = Col("Location")
        error_count = Col("Error count")

    data_dict = dict()

    for device in data.index.levels[0]:
        device_data = data.loc[device] \
            .reset_index() \
            .sort_values(by='date', ascending=False)
        device_data['device'] = device
        data_dict[device] = HeatmapTable(device_data.to_dict(orient='records'))

    return render_template("errors.html", data=data_dict, messages="Errors by file location")


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/system/crashes')
def crashes():
    def _plot(device):
        return PlotCrashes(plot_parameters={'device': device})

    ajax_plot_list = [_plot(device) for device in get_devices()]

    return render_template('crashes.html',
                           ajax_plot_list=ajax_plot_list,
                           js_resources=INLINE.render_js(),
                           css_resources=INLINE.render_css()
                           )

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/logs/<device>', methods=['GET'])
@app.route('/logs/<device>/<int:duration>', methods=['GET'])
@app.route('/logs/<device>/<int:duration>/<log_level>', methods=['GET'])
@app.route('/logs/<device>/<int:duration>/<log_level>/<timestamp>/', methods=['GET'])
def show_logs(device, duration=5, timestamp=None, log_level="TRACE"):
    try:
        page = int(request.args.get('page', default=1, type=int))
    except ValueError:
        logging.error(f"get value page={page} is not an integer")
        page = 1

    filename = request.args.get('filename', default=None)
    line_number = request.args.get('line_number', type=int, default=None)

    if not timestamp:
        timestamp = datetime.now()
    log_text, pagination = fetch_logs(device, timestamp, log_level, before=duration, after=2, page=page,
                                      filename=filename, line_number=line_number)
    devices = Dashboard().devices()
    return render_template("device_log.html", devices=devices, log_text=log_text, device=device, pagination=pagination)


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/system/version', methods=['GET'])
def version_messages():
    device_id = request.args.get('device', default="", type=str)
    errors = Errors()
    data = errors.version(device_id=device_id)

    class VersionTable(Table):
        classes = ["error-table"]
        timestamp = LinkCol('Time', 'show_logs',
                            url_kwargs=dict(device='device', timestamp='timestamp'),
                            url_kwargs_extra=dict(log_level='TRACE', duration=5),
                            attr='timestamp')
        ip = Col('IP Address')
        commit = Col('Commit')
        branch = Col('branch')
        version_timestamp = Col('Version Timestamp')
        crash = CrashCol('Crash')

    data_dict = dict()

    for device in data.index.levels[0]:
        device_data = data.loc[device] \
            .sort_values(by='timestamp', ascending=False)
        device_data['device'] = device
        data_dict[device] = VersionTable(device_data.to_dict(orient='records'))

    return render_template("errors.html", data=data_dict, messages="System start")


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/_monitor_device', methods=['POST'])
def _monitor_device():
    device = ""
    limit = False
    log_level = "TRACE"
    if request.method == 'POST':
        device = request.form.get('device')
        limit = request.form.get('limit')
        log_level = request.form.get('log_level')
        if limit == "true":
            limit = True
        else:
            limit = False

    logging.info(f"_monitor: device={device}, limit={limit}, log_level={log_level}")
    if limit:
        num_lines = 35
    else:
        num_lines = 50000

    start_date = datetime.now() - timedelta(days=1)
    logs, pagination = Errors().logs(device_id=device, since=start_date, num_lines=num_lines, log_level=log_level)

    log_text = format_logs(logs, device=device)

    if limit:
        title = f"Start monitoring device {device} ..."
    else:
        title = f"Load logs for device {device} ..."

    return jsonify(title=title, result=f"<pre>{log_text}</pre>")


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/monitor')
def monitor():
    devices = Dashboard().devices()
    return render_template("monitor.html", devices=devices)


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/statistics/mode')
def statistics_mode():
    data = ModeStatistics().mode_counts()
    labels = ["Auto", "Off", "Manual", "Light Shower"]
    return render_template('statistics_mode.html', data=data, labels=jsonify(labels))


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/statistics/mouse', methods=['GET'])
def statistics_mouse():
    start_date, end_date = parse_date_range(request)
    no_data = dict(stats="", plot_distance="", plot_speed="", plot_deviation="")

    mouse_data = MouseData().gesture_data(start_date, end_date)

    statistics_data = {}
    scripts = []
    for device, data in mouse_data.items():
        if data.count()[0] > 0:
            fig_distance = plot_histogram(data.distance.dropna(),
                                          x_axis_label="Mouse distance", y_axis_label="Amount",
                                          plot_width=300, plot_height=400
                                          )
            script, div_distance = components(fig_distance)
            scripts.append(script)

            fig_speed = plot_histogram(data.speed.dropna(),
                                       x_axis_label="Mouse speed", y_axis_label="Amount",
                                       plot_width=300, plot_height=400, fill_color='blue'
                                       )
            script, div_speed = components(fig_speed)
            scripts.append(script)

            fig_deviation = plot_histogram(data.deviation.dropna(),
                                           x_axis_label="Gesture deviation", y_axis_label="Amount",
                                           plot_width=300, plot_height=400, fill_color='orange'
                                           )
            script, div_deviation = components(fig_deviation)
            scripts.append(script)

            stats = data.describe().to_html()
            statistics_data[device] = dict(stats=stats,
                                           plot_distance=div_distance,
                                           plot_speed=div_speed,
                                           plot_deviation=div_deviation)

        else:
            statistics_data[device] = no_data

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    return render_template("statistics_mouse.html",
                           timespan=humanfriendly.format_timespan(end_date - start_date, max_units=2),
                           data=statistics_data,
                           scripts=scripts,
                           js_resources=js_resources,
                           css_resources=css_resources)


# ----------------------------------------------------------------------------------------------------------------------


def parse_date_range(request) -> Tuple[datetime, datetime]:
    start_str = request.args.get('start', default="", type=str)
    end_str = request.args.get('end', default="", type=str)

    if not end_str:
        end_date = datetime.now()
    else:
        end_date = dateutil.parser.parse(end_str)

    if not start_str:
        start_date = end_date - timedelta(days=1)
    else:
        start_date = dateutil.parser.parse(start_str)

    logging.debug(f"Date range: {start_str} -- {end_str}\n"
                  f"Parsed Date range: {start_date} -- {end_date}")
    return start_date, end_date


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/statistics/database_delay', methods=['GET'])
def statistics_database_delay():
    start_date, end_date = parse_date_range(request)

    def _plot(device):
        return PlotDatabaseDelay(plot_parameters={'start_date': start_date,
                                                  'end_date': end_date,
                                                  'device': device})

    ajax_plot_list = [_plot(device) for device in get_devices()]

    return render_template("statistics_database_delay.html",
                           timespan=humanfriendly.format_timespan(end_date - start_date, max_units=2),
                           ajax_plot_list=ajax_plot_list,
                           js_resources=INLINE.render_js(),
                           css_resources=INLINE.render_css()
                           )

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/database/size')
def database_size():
    ajax_plot_list = [PlotDatabaseSize(plot_parameters={})]

    return render_template('database_size.html',
                           database_plot=ajax_plot_list[0],
                           ajax_plot_list=ajax_plot_list,
                           js_resources=INLINE.render_js(),
                           css_resources=INLINE.render_css()
                           )

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/statistics/switch_cycles')
def statistics_switch_cycles():
    def _plot(device):
        return PlotOnOffCycles(plot_parameters={'device': device})

    ajax_plot_list = [_plot(device) for device in get_devices()]

    return render_template('statistics_on_off.html',
                           ajax_plot_list=ajax_plot_list,
                           js_resources=INLINE.render_js(),
                           css_resources=INLINE.render_css()
                           )

# ----------------------------------------------------------------------------------------------------------------------


def create_timeseries(sensor_data, sensor: str, unit: str, time_range: Tuple[datetime, datetime], **kwargs):
    connectivity_data = kwargs.pop('connectivity_data', None)
    # If no sensor_key is given, use the lower case sensor name
    sensor_key = kwargs.pop("sensor_key", sensor).lower()
    start_date, end_date = time_range
    figures = []
    devices = []
    x_range = (start_date, end_date)
    for device, data in sensor_data.items():
        if not data.empty:
            fig = plot_time_series(data.timestamp,
                                   data[[sensor_key]].iloc[:, 0],
                                   x_range=x_range,
                                   y_axis_label=unit,
                                   mode='step')
            x_range = fig.x_range
            if connectivity_data is not None:
                try:
                    device_data = connectivity_data.loc[device]
                    connectivity_fig = plot_connection_times(device_data, x_range=fig.x_range)
                    fig = column(fig, connectivity_fig)
                except KeyError:
                    logging.warning(f"No connectivity data for device {device}.")
            figures.append(fig)
            devices.append(device)

    script, divs = components(figures)
    plot_divs = dict(zip(devices, divs))

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    html = render_template(
        'sensors_timeseries.html',
        timespan=humanfriendly.format_timespan(end_date - start_date, max_units=2),
        sensor=sensor,
        unit=unit,
        plot_script=script,
        plot_divs=plot_divs,
        js_resources=js_resources,
        css_resources=css_resources,
    )

    return html


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/device/<device>', methods=['GET'])
def sensors_device(device):
    start_date, end_date = parse_date_range(request)
    x_range = (start_date, end_date)
    figures = {}
    sensor = SensorData()

    connectivity_data = Connectivity.connection_times(start_date, end_date, device)
    fig = plot_connection_times(connectivity_data, x_range=x_range, title="Internet connection")
    x_range = fig.x_range
    figures['connectivity'] = fig

    sensor_data = PresenceDetectorStatistics().on_off_timeseries(start_date, end_date, device)
    fig = plot_on_off_times(sensor_data, x_range=x_range, title="Light On/Off")
    x_range = fig.x_range
    figures['on_off'] = fig

    sensor_data = sensor.temperature(start_date, end_date, device)[device]
    fig = plot_time_series(sensor_data.timestamp,
                           sensor_data.temperature,
                           x_range=x_range,
                           title="Temperature",
                           y_axis_label="°C")
    x_range = fig.x_range
    figures['temperature'] = fig

    sensor_data = sensor.humidity(start_date, end_date, device)[device]
    fig = plot_time_series(sensor_data.timestamp,
                           sensor_data.humidity,
                           x_range=x_range,
                           title="Humidity",
                           y_axis_label="%RH")
    figures['humidity'] = fig

    sensor_data = sensor.pressure(start_date, end_date, device)[device]
    fig = plot_time_series(sensor_data.timestamp,
                           sensor_data.pressure,
                           x_range=x_range,
                           title="Pressure",
                           y_axis_label="hPa")
    figures['pressure'] = fig

    sensor_data = sensor.brightness(start_date, end_date, device).loc[device]
    figures_brightness = timeseries_plot_brightness(sensor_data,
                                                    unit="lx",
                                                    x_range=x_range)

    for key, fig in figures_brightness.items():
        figures[key] = fig

    sensor_data = sensor.gas(start_date, end_date, device)[device]
    fig = plot_time_series(sensor_data.timestamp,
                           sensor_data.amount,
                           x_range=x_range,
                           title="Gas (VOC)",
                           y_axis_label="kOhm")
    figures['gas'] = fig

    plot = column(*list(figures.values()))

    # plot = column(figures['temperature'],
    #              figures['humidity'],
    #              figures['pressure'],
    #              figures['gas'])
    plot_scripts, plot_divs = components(plot)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    html = render_template(
        'device_sensors_timeseries.html',
        timespan=humanfriendly.format_timespan(end_date - start_date, max_units=2),
        device=device,
        plot_scripts=plot_scripts,
        plot_divs=plot_divs,
        js_resources=js_resources,
        css_resources=css_resources,
    )

    return html


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/debug/sensors/presence', methods=['GET'])
def debug_sensors_presence():
    start_date, end_date = parse_date_range(request)
    x_range = start_date, end_date
    debug_on_off_data = PresenceDetectorStatistics().debug_on_off_timeseries(start_date, end_date)
    on_off_data = PresenceDetectorStatistics().on_off_timeseries(start_date, end_date).dropna()
    connectivity_data = Connectivity.connection_times(start_date, end_date)

    figures = []
    devices = []

    # If no sensor_key is given, use the lower case sensor name
    for device in on_off_data.index.levels[0]:
        device_data = on_off_data.loc[device]
        debug_device_data = debug_on_off_data.loc[device]
        figures_device = []
        if not device_data.empty:
            fig = plot_on_off_times(device_data, x_range=x_range)
            figures_device.append(fig)
            x_range = fig.x_range

            fig_debug = plot_time_series(debug_device_data.timestamp,
                                   debug_device_data[['value']].iloc[:, 0],
                                   x_range=x_range,
                                   y_axis_label="on/off",
                                   mode='marker')
            figures_device.append(fig_debug)
            if connectivity_data is not None:
                try:
                    device_data = connectivity_data.loc[device]
                    connectivity_fig = plot_connection_times(device_data, x_range=x_range)
                    figures_device.append(connectivity_fig)

                except KeyError:
                    logging.warning(f"No connectivity data for device {device}.")
            if len(figures_device) > 1:
                fig = column(*figures_device)
            figures.append(fig)
            devices.append(device)

    plot_script, divs = components(figures)
    plot_divs = dict(zip(devices, divs))

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    html = render_template(
        'sensors_timeseries.html',
        timespan=humanfriendly.format_timespan(end_date - start_date, max_units=2),
        sensor="Presence",
        unit="on/off",
        plot_script=plot_script,
        plot_divs=plot_divs,
        js_resources=js_resources,
        css_resources=css_resources,
    )

    return html

# ----------------------------------------------------------------------------------------------------------------------


def create_sensor_view(device: str, start_date: date, end_date: date, sensor: str, sample_rate: str):
    all_sensors = ["temperature", "humidity", "pressure", "brightness", "gas", "presence"]
    if sensor == "ALL":
        active_sensors = all_sensors
    else:
        active_sensors = [sensor]

    def _plot(device):
        return PlotSensors(plot_parameters={'start_date': start_date,
                                            'end_date': end_date,
                                            'device': device,
                                            'sensors': active_sensors,
                                            'sample_rate': sample_rate})

    if device == "ALL":
        devices = get_devices()
    else:
        devices = [device]

    ajax_plot_list = [_plot(device) for device in devices]

    return render_template("sensors_timeseries_new.html",
                           device=device,
                           sensor=sensor,
                           sample_rate=sample_rate,
                           automatic_sample_rate=PlotSensors.auto_sample_rate(start_date, end_date),
                           start_date=format_datetime(start_date),
                           end_date=format_datetime(end_date),
                           all_sensors=all_sensors,
                           all_devices=get_devices(),
                           all_sample_rates=PlotSensors.supported_sample_rates(),
                           ajax_plot_list=ajax_plot_list,
                           js_resources=INLINE.render_js(),
                           css_resources=INLINE.render_css()
                           )

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/analytics/sensor')
@app.route('/analytics/sensor/<device>/<sensor>/<sample_rate>/<start_date>/<end_date>')
def analytics_sensor(device: Optional[str] = None,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None,
                     sensor: str = "temperature",
                     sample_rate: str = "AUTO"):
    logging.warning(f"{start_date} - {end_date}")
    if not end_date or not start_date:
        start_date = date.today() - timedelta(days=1)
        end_date = date.today() - timedelta(days=1)
    else:
        from utils.date import parse_date
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

    if not device:
        device = "ALL"

    return create_sensor_view(device,
                              start_date,
                              end_date,
                              sensor,
                              sample_rate=sample_rate)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/analytics/connection')
def analytics_connection():
    def _plot(device):
        return PlotConnection(plot_parameters={'device': device})

    ajax_plot_list = [_plot(device) for device in get_devices()]

    return render_template('analytics_connection.html',
                           ajax_plot_list=ajax_plot_list,
                           js_resources=INLINE.render_js(),
                           css_resources=INLINE.render_css()
                           )


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/analytics/keyboard')
def analytics_keyboard():
    def _plot(device):
        return PlotKeyboard(plot_parameters={'device': device})

    ajax_plot_list = [_plot(device) for device in get_devices()]

    return render_template('analytics_keyboard.html',
                           ajax_plot_list=ajax_plot_list,
                           js_resources=INLINE.render_js(),
                           css_resources=INLINE.render_css()
                           )


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/analytics/keypress')
def analytics_keypress():
    def _plot(device):
        return PlotKeypress(plot_parameters={'device': device})

    ajax_plot_list = [_plot(device) for device in get_devices()]

    return render_template('analytics_keypress.html',
                           ajax_plot_list=ajax_plot_list,
                           js_resources=INLINE.render_js(),
                           css_resources=INLINE.render_css()
                           )

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/analytics/mouse')
def analytics_mouse():
    def _plot(device):
        return PlotMouse(plot_parameters={'device': device})

    ajax_plot_list = [_plot(device) for device in get_devices()]

    return render_template('analytics_mouse.html',
                           ajax_plot_list=ajax_plot_list,
                           js_resources=INLINE.render_js(),
                           css_resources=INLINE.render_css()
                           )


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/presence', methods=['GET'])
def sensors_presence():
    start_date, end_date = parse_date_range(request)
    x_range = start_date, end_date
    on_off_data = PresenceDetectorStatistics().on_off_timeseries(start_date, end_date)
    connectivity_data = Connectivity.connection_times(start_date, end_date)

    figures = []
    devices = []

    # If no sensor_key is given, use the lower case sensor name
    for device in on_off_data.index.levels[0]:
        try:
            device_data = on_off_data.loc[device]
            fig = plot_on_off_times(device_data, x_range=x_range)
            x_range = fig.x_range
            if connectivity_data is not None:
                try:
                    device_data = connectivity_data.loc[device]
                    connectivity_fig = plot_connection_times(device_data, x_range=x_range)
                    fig = column(fig, connectivity_fig)
                except KeyError:
                    logging.warning(f"No connectivity data for device {device}.")
            figures.append(fig)
            devices.append(device)
        except KeyError:
            logging.warning(f"No on_of_data for device: {device}")

    plot_script, divs = components(figures)
    plot_divs = dict(zip(devices, divs))

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    html = render_template(
        'sensors_timeseries.html',
        timespan=humanfriendly.format_timespan(end_date - start_date, max_units=2),
        sensor="Presence",
        unit="on/off",
        plot_script=plot_script,
        plot_divs=plot_divs,
        js_resources=js_resources,
        css_resources=css_resources,
    )

    return html


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/temperature', methods=['GET'])
def sensors_temperature():
    start_date, end_date = parse_date_range(request)
    sensor_data = SensorData().temperature(start_date, end_date)
    connectivity_data = Connectivity.connection_times(start_date, end_date)

    return create_timeseries(sensor_data,
                             sensor="Temperature",
                             unit="°C",
                             time_range=(start_date, end_date),
                             connectivity_data=connectivity_data)


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/humidity', methods=['GET'])
def sensors_humidity():
    start_date, end_date = parse_date_range(request)
    sensor_data = SensorData().humidity(start_date, end_date)
    connectivity_data = Connectivity.connection_times(start_date, end_date)

    return create_timeseries(sensor_data,
                             sensor="Humidity",
                             unit="%RH",
                             time_range=(start_date, end_date),
                             connectivity_data=connectivity_data)


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/pressure', methods=['GET'])
def sensors_pressure():
    start_date, end_date = parse_date_range(request)
    sensor_data = SensorData().pressure(start_date, end_date)
    connectivity_data = Connectivity.connection_times(start_date, end_date)

    return create_timeseries(sensor_data,
                             sensor="Pressure",
                             unit="hPa",
                             time_range=(start_date, end_date),
                             connectivity_data=connectivity_data)


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/gas', methods=['GET'])
def sensors_gas():
    start_date, end_date = parse_date_range(request)
    sensor_data = SensorData().gas(start_date, end_date)
    connectivity_data = Connectivity.connection_times(start_date, end_date)

    return create_timeseries(sensor_data,
                             sensor="Gas",
                             sensor_key="amount",
                             unit="VOC kOhm",
                             time_range=(start_date, end_date),
                             connectivity_data=connectivity_data)


# ----------------------------------------------------------------------------------------------------------------------


def timeseries_plot_brightness(device_data, unit: str, x_range, **kwargs):
    sensor_id_dict = {"brightness_r_h@BH1750": "RH",
                      "brightness_r_v@BH1750": "RV",
                      "brightness_l_h@BH1750": "LH",
                      "brightness_l_v@BH1750": "LV"}
    device_data = device_data.dropna()

    # re-index the data set of each single device
    # so that sensor_ids only contains items that are
    # included in the data set of this particular device
    device_data = device_data.set_index(device_data.index)
    sensor_ids = device_data.index.levels[0]
    figures = {}
    # loop over all 4 brightness sensors
    # if data for this sensor is available
    for sensor_id in sensor_ids:
        data = device_data.loc[sensor_id]
        data = data.sort_values(by=['timestamp'])

        time_series = data.brightness
        timestamp = data.timestamp

        # Convert sensor name to shorter form
        sensor_name = sensor_id_dict.get(sensor_id, sensor_id)

        fig = plot_time_series(timestamp, time_series,
                               x_range=x_range,
                               title=f"Brightness ({sensor_name})", y_axis_label=unit)
        x_range = fig.x_range

        figures[f'brightness_{sensor_name}'] = fig

    return figures


# ----------------------------------------------------------------------------------------------------------------------


def create_timeseries_brightness(sensor_data,
                                 sensor: str,
                                 unit: str,
                                 time_range: Tuple[datetime, datetime],
                                 **kwargs):
    sensor_id_dict = {"brightness_r_h@BH1750": "RH",
                      "brightness_r_v@BH1750": "RV",
                      "brightness_l_h@BH1750": "LH",
                      "brightness_l_v@BH1750": "LV"}

    # If no sensor_key is given, use the lower case sensor name
    sensor_key = kwargs.get("sensor_key", sensor).lower()

    connectivity_data = kwargs.pop('connectivity_data', None)

    start_date, end_date = time_range
    x_range = (start_date, end_date)

    figures = []
    devices_list = []

    # loop over all devices
    devices = sensor_data.index.levels[0]
    for device in devices:
        device_data = sensor_data.loc[device].dropna()

        # re-index the data set of each single device
        # so that sensor_ids only contains items that are
        # included in the data set of this particular device
        device_data = device_data.set_index(device_data.index)
        sensor_ids = device_data.index.levels[0]
        figures_device = []
        # loop over all 4 brightness sensors
        # if data for this sensor is available
        for sensor_id in sensor_ids:
            data = device_data.loc[sensor_id]
            data = data.sort_values(by=['timestamp'])

            time_series = data[[sensor_key]].iloc[:, 0]
            timestamp = data.timestamp

            # Convert sensor name to shorter form
            sensor_name = sensor_id_dict.get(sensor_id, sensor_id)

            fig = plot_time_series(timestamp, time_series,
                                   x_range=x_range,
                                   title=f"Sensor: {sensor_name}",
                                   mode="step")
            x_range = fig.x_range

            figures_device.append(fig)

        if connectivity_data is not None:
            try:
                device_data = connectivity_data.loc[device]
                connectivity_fig = plot_connection_times(device_data, x_range=x_range)
                figures_device.append(connectivity_fig)
            except KeyError:
                logging.warning(f"No connectivity data for device {device}.")

        figures.append(column(*figures_device))
        devices_list.append(device)

    plot_script, divs = components(figures)
    plot_divs = dict(zip(devices_list, divs))

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    html = render_template(
        'sensors_timeseries.html',
        timespan=humanfriendly.format_timespan(end_date - start_date, max_units=2),
        sensor=sensor,
        unit=unit,
        plot_script=plot_script,
        plot_divs=plot_divs,
        js_resources=js_resources,
        css_resources=css_resources,
    )

    return html


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/brightness', methods=['GET'])
def sensors_brightness():
    start_date, end_date = parse_date_range(request)
    sensor_data = SensorData().brightness(start_date, end_date)
    connectivity_data = Connectivity.connection_times(start_date, end_date)

    return create_timeseries_brightness(sensor_data,
                                        sensor="Brightness",
                                        unit="lx",
                                        time_range=(start_date, end_date),
                                        connectivity_data=connectivity_data)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/_get_plot', methods=['POST'])
def _get_plot():
    if request.method != 'POST':
        return ""

    json_data = request.get_json()
    plot = AjaxFactory.create_plot(json_data)
    plot.render()
    return plot.json_data()

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/_download_data', methods=['POST'])
def _download_data():
    if request.method != 'POST':
        return ""

    json_data = request.get_json()
    plot = AjaxFactory.create_plot(json_data)
    data = plot.fetch_data()
    json_data = dict(filename="data.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     bytes=b64encode(convert_to_excel(data)).decode('ascii'))
    return jsonify(json_data)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/analytics/scenes')
def analytics_scenes():
    def _plot(device):
        return PlotSceneDurations(plot_parameters={'device': device})

    ajax_plot_list = [_plot(device) for device in get_devices()]

    return render_template('analytics_scene.html',
                           ajax_plot_list=ajax_plot_list,
                           js_resources=INLINE.render_js(),
                           css_resources=INLINE.render_css()
                           )

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/clustering/input_distribution')
def clustering_input_distribution():
    def _plot(device):
        return PlotClusteringInputDistribution(plot_parameters={'device': device})

    ajax_plot_list = [_plot(device) for device in get_devices()]

    return render_template('clustering_input_distribution.html',
                           ajax_plot_list=ajax_plot_list
                           )

# ----------------------------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=Config.debug)

# ----------------------------------------------------------------------------------------------------------------------
