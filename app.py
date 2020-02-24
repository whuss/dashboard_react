import os
from flask import Flask, render_template, jsonify, request
from flask_table import Table, Col


from bokeh.embed import components
from bokeh.layouts import column
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from typing import Tuple

from dataclasses import dataclass
from datetime import datetime, timedelta

from data import Articles

from db import session, Errors, Dashboard, SensorData, ModeStatistics
from db import MouseData, PresenceDetectorStatistics, DatabaseDelay

import humanfriendly

from plots import plot_histogram, plot_duration_histogram, plot_time_series, plot_on_off_cycles

# ----------------------------------------------------------------------------------------------------------------------

app = Flask(__name__)

# ----------------------------------------------------------------------------------------------------------------------

@app.teardown_request
def teardown(exception=None):
    # teardown database session
    session.close()

# ----------------------------------------------------------------------------------------------------------------------

@app.context_processor
def utility_processor():
    def _str(input):
        return str(input) if input else ""

    def _time_span(input):
        if input:
            seconds = input.seconds
            minutes = seconds // 60
            seconds = seconds % 60
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours:02}:{minutes:02}:{seconds:02}"
            #return humanfriendly.format_timespan(input, max_units=2)
        return ""

    def _number(input):
        return input if input else ""

    def _unit(input, unit):
        if not input:
            return ""
        return f"{input:.2f} {unit}"

    return dict(_str=_str,
                _time_span=_time_span,
                _number=_number,
                _unit=_unit)


# ----------------------------------------------------------------------------------------------------------------------

@app.route('/')
def index():
    dash = Dashboard()
    start_date = datetime.now() - timedelta(days=7)
    dashboard = dash.dashboard(start_date)
    return render_template('home.html', dashboard=dashboard)

# ----------------------------------------------------------------------------------------------------------------------


class PreCol(Col):
    """Column class for Flask Table that wraps its content in a pre tag"""
    def td_format(self, content):
        return f'''<pre style="text-align: left; width: 75%; white-space: pre-line;">
                       {content}
                   </pre>'''

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/system/errors', methods=['GET'])
def error_messages():
    device_id = request.args.get('id', default="", type=str)
    data = Errors().errors(device_id=device_id)

    class ErrorTable(Table):
        classes = ["error-table"]
        timestamp = Col('Time')
        service = Col('Service')
        errno = Col('Error Number')
        message = PreCol('Error Message')

    data_dict = dict()

    for device in data.index.levels[0]:
        data_dict[device] = ErrorTable(data.loc[device]
                                           .sort_values(by='timestamp', ascending=False)
                                           .to_dict(orient='records'))

    return render_template("errors.html", route='/system/errors', data=data_dict, messages="Error messages")


# ----------------------------------------------------------------------------------------------------------------------

@app.route('/system/logs', methods=['GET'])
def log_messages():
    device_id = request.args.get('id', default="", type=str)
    data = Errors().logs(device_id=device_id)

    class LogsTable(Table):
        classes = ["error-table"]
        timestamp = Col('Time')
        filename = Col('Filename')
        line_number = Col('Line Number')
        log_level = Col('Log Level')
        message = PreCol('Error Message')

    data_dict = dict()

    for device in data.index.levels[0]:
        data_dict[device] = LogsTable(data.loc[device]
                                          .sort_values(by='timestamp', ascending=False)
                                          .to_dict(orient='records'))

    return render_template("errors.html", route='/system/logs', data=data_dict, messages="Log messages")

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/system/version', methods=['GET'])
def version_messages():
    device_id = request.args.get('id', default = "", type = str)
    data = Errors().version(device_id=device_id)

    class VersionTable(Table):
        classes = ["error-table"]
        timestamp = Col('Time')
        commit = Col('Commit')
        branch = Col('branch')
        version_timestamp = Col('Version Timestamp')

    data_dict = dict()

    for device in data.index.levels[0]:
        data_dict[device] = VersionTable(data.loc[device]
                                             .sort_values(by='timestamp', ascending=False)
                                             .to_dict(orient='records'))

    return render_template("errors.html", route='/system/version', data=data_dict, messages="System start")

# ----------------------------------------------------------------------------------------------------------------------


def format_logs(logs):
    log_text = ""
    for index, lp in logs.iterrows():
        filename = os.path.basename(lp.filename)
        header_no_format = f'({lp.timestamp}) {lp.log_level:<8} [{filename}:{lp.line_number}]: '
        header = f'({lp.timestamp}) <span class="{lp.log_level}">{lp.log_level:<8}</span> [<span data-toggle="tooltip" title="{lp.filename}" >{filename}</span>:{lp.line_number}]: '
        identation = len(header_no_format) * " "
        message_lines = lp.message.split("\n")
        formatted_message = header + message_lines[0] + "\n" + \
            "\n".join([identation + line for line in message_lines[1:]])

        if len(message_lines) > 1:
            formatted_message += "\n"

        log_text += formatted_message

    return log_text

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/_monitor_device', methods=['POST'])
def _monitor_device():
    device = ""
    if request.method == 'POST':
        device = request.form.get('device')
    print(f"_monitor: {device}")

    start_date = datetime.now() - timedelta(days=1)
    logs = Errors().logs(device_id=device, since=start_date)

    log_text = format_logs(logs)

    return jsonify(result=f"Start monitoring {device}\n<pre>{log_text}</pre>")

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/monitor')
def monitor():
    devices = Dashboard().devices()
    for device in devices:
        print(device)
    return render_template("monitor.html", devices=devices)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/statistics/mode')
def statistics_mode():
    data = ModeStatistics().mode_counts()
    labels = ["Auto", "Off", "Manual", "Light Shower"]
    return render_template('statistics_mode.html', data=data, labels=jsonify(labels))

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/statistics/mouse')
def statistics_mouse():
    no_data = dict(stats="", plot_distance="", plot_speed="", plot_deviation="")

    start_date = datetime.now() - timedelta(days=14)
    mouse_data = MouseData().gesture_data(start_date)

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
                           data=statistics_data,
                           scripts=scripts,
                           js_resources=js_resources,
                           css_resources=css_resources)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/statistics/database_delay', methods=['GET'])
def statistics_database_delay():
    start_str = request.args.get('start', default = "", type = str)
    end_str = request.args.get('end', default = "", type = str)
    from dateutil.parser import parse

    if not end_str:
        end_date = datetime.now()
    else:
        end_date = parse(end_str)

    if not start_str:
        start_date = end_date - timedelta(days=1)
    else:
        start_date = parse(start_str)

    print(f"Date range: {start_str} -- {end_str}")
    print(f"Parsed Date range: {start_date} -- {end_date}")

    data = DatabaseDelay().package_delay(start_date, end_date)

    print("Query finished")

    figures = {}
    scripts = []

    # compute time range
    x_range = min(data.delay), max(data.delay)

    for device in data.index.levels[0]:
        device_data = data.loc[device].delay.dropna()

        fig = plot_duration_histogram(device_data, time_scale="m",
                x_axis_label="Package delay", y_axis_label="Amount",
                plot_width=600, plot_height=400
            )
        script, div = components(fig)
        figures[device] = div
        scripts.append(script)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    return render_template("statistics_database_delay.html",
                           timespan=humanfriendly.format_timespan(end_date-start_date, max_units=2),
                           figures=figures,
                           scripts=scripts,
                           js_resources=js_resources,
                           css_resources=css_resources)


# ----------------------------------------------------------------------------------------------------------------------

@app.route('/statistics/switch_cycles')
def statistics_switch_cycles():
    data = PresenceDetectorStatistics().on_off_cycle_count()

    figures = {}
    scripts = []

    # compute time range
    dates = data.reset_index().date
    x_range = min(dates), max(dates)

    for device in data.index.levels[0]:
        device_data = data.loc[device].reset_index()
        fig = plot_on_off_cycles(device_data, x_range=x_range)
        script, div = components(fig)
        figures[device] = div
        scripts.append(script)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    return render_template("statistics_on_off.html",
                           figures=figures,
                           scripts=scripts,
                           js_resources=js_resources,
                           css_resources=css_resources)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors')
def sensors():
    sensor_data = SensorData().current_sensor_data()

    return render_template('sensors.html', sensors=sensor_data)



# ----------------------------------------------------------------------------------------------------------------------


def create_timeseries(sensor_data, sensor: str, unit: str, time_range: Tuple[datetime, datetime], **kwargs):
    # If no sensor_key is given, use the lower case sensor name
    sensor_key = kwargs.pop("sensor_key", sensor).lower()
    start_date, end_date = time_range
    plot_scripts = {}
    plot_divs = {}
    x_range = (start_date, end_date)
    for device, data in sensor_data.items():
        fig = plot_time_series(data.timestamp, data[[sensor_key]].iloc[:, 0], x_range=x_range, **kwargs)
        if fig:
            script, div = components(fig)
        else:
            script, div = "", ""
        plot_scripts[device] = script
        plot_divs[device] = div

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    html = render_template(
        'sensors_timeseries.html',
        timespan=humanfriendly.format_timespan(end_date-start_date, max_units=2),
        sensor=sensor,
        unit=unit,
        plot_scripts=plot_scripts,
        plot_divs=plot_divs,
        js_resources=js_resources,
        css_resources=css_resources,
    )

    return encode_utf8(html)

# ----------------------------------------------------------------------------------------------------------------------

@app.route('/sensors/presence')
def sensors_presence():
    now = datetime.now()
    start_date = now - timedelta(days=14)

    on_off_data = PresenceDetectorStatistics().on_off_timeseries(start_date)

    return create_timeseries(on_off_data, sensor="Presence detected", sensor_key="value",
                             unit="on", time_range=(start_date, now), mode="step")

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/temperature')
def sensors_temp():
    now = datetime.now()
    start_date = now - timedelta(days=14)
    sensor_data = SensorData().temperature(start_date)

    return create_timeseries(sensor_data, sensor="Temperature", unit="°C", time_range=(start_date, now))

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/humidity')
def sensors_humidity():
    now = datetime.now()
    start_date = now - timedelta(days=14)
    sensor_data = SensorData().humidity(start_date)

    return create_timeseries(sensor_data, sensor="Humidity", unit="%RH", time_range=(start_date, now))

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/pressure')
def sensors_pressure():
    now = datetime.now()
    start_date = now - timedelta(days=14)
    sensor_data = SensorData().pressure(start_date)

    return create_timeseries(sensor_data, sensor="Pressure", unit="hPa", time_range=(start_date, now))

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/gas')
def sensors_gas():
    now = datetime.now()
    start_date = now - timedelta(days=14)
    sensor_data = SensorData().gas(start_date)

    return create_timeseries(sensor_data, sensor="Gas", sensor_key="amount", unit="VOC kOhm", time_range=(start_date, now))

# ----------------------------------------------------------------------------------------------------------------------


def create_timeseries_brightness(sensor_data, sensor: str, unit: str, time_range: Tuple[datetime, datetime], **kwargs):
    sensor_id_dict = {"brightness_r_h@BH1750": "RH",
                          "brightness_r_v@BH1750": "RV",
                          "brightness_l_h@BH1750": "LH",
                          "brightness_l_v@BH1750": "LV"}

    # If no sensor_key is given, use the lower case sensor name
    sensor_key = kwargs.get("sensor_key", sensor).lower()
    start_date, end_date = time_range
    plot_scripts = {}
    plot_divs = {}

    # loop over all devices
    devices = sensor_data.index.levels[0]
    for device in devices:
        device_data = sensor_data.loc[device].dropna()
        script, div = "", ""

        # re-index the data set of each single device
        # so that sensor_ids only contains items that are
        # included in the data set of this particular device
        device_data = device_data.set_index(device_data.index)
        sensor_ids = device_data.index.levels[0]
        figures = []
        x_range = None
        # loop over all 4 brightness sensors
        # if data for this sensor is available
        for sensor_id in sensor_ids:
            if not x_range:
                x_range = (start_date, end_date)
            data = device_data.loc[sensor_id]
            data = data.sort_values(by=['timestamp'])

            time_series = data[[sensor_key]].iloc[:, 0]
            timestamp = data.timestamp

            # Convert sensor name to shorter form
            sensor_name = sensor_id_dict.get(sensor_id, sensor_id)

            fig = plot_time_series(timestamp, time_series,
                                   x_range=x_range,
                                   title=f"Sensor: {sensor_name}")
            x_range = fig.x_range

            figures.append(fig)

        plot = column(*figures)
        _script, _div = components(plot)
        script += _script
        div += _div

        plot_scripts[device] = script
        plot_divs[device] = div

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    html = render_template(
        'sensors_timeseries.html',
        timespan=humanfriendly.format_timespan(end_date-start_date, max_units=2),
        sensor=sensor,
        unit=unit,
        plot_scripts=plot_scripts,
        plot_divs=plot_divs,
        js_resources=js_resources,
        css_resources=css_resources,
    )

    return encode_utf8(html)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/brightness')
def sensors_brightness():
    now = datetime.now()
    start_date = now - timedelta(days=14)
    sensor_data = SensorData().brightness(start_date)

    return create_timeseries_brightness(sensor_data, sensor="Brightness", unit="lx", time_range=(start_date, now))

# ----------------------------------------------------------------------------------------------------------------------
# Test routes
# ----------------------------------------------------------------------------------------------------------------------

# Declare your table
class ItemTable(Table):
    name = Col('Name')
    description = Col('Description')

# Get some objects
class Item(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description
items = [Item('Name1', 'Description1'),
         Item('Name2', 'Description2'),
         Item('Name3', 'Description3')]

@app.route("/table_test")
def table_test():

    table = ItemTable(items)
    return render_template("table.html", table=table)

@app.route("/simple_chart")
def chart():
    legend = 'Monthly Data'
    labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    values = [10, 9, 8, 7, 6, 4, 7, 8]
    return render_template('charts.html', values=values, labels=labels, legend=legend)


@app.route("/pie_chart")
def pie_chart():
    legend = 'Monthly Data'
    labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    values = [10, 9, 8, 7, 6, 4, 7, 8]
    return render_template('pie_charts.html', values=values, labels=labels, legend=legend)


Articles = Articles()

@app.route('/articles')
def articles():
    return render_template('articles.html', articles=Articles)

@app.route('/test_post', methods=["GET"])
def test_post():
    start = request.args.get('start', default = "", type = str)
    end = request.args.get('end', default = "", type = str)
    print(f"Got data: {start} -- {end}")
    return f"data: {start} -- {end}"


# ----------------------------------------------------------------------------------------------------------------------

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id)

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)