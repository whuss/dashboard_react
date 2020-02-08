# Video: https://www.youtube.com/watch?v=zRwy8gtgJ1A
# Code from: https://github.com/bradtraversy/myflaskapp

from flask import Flask, render_template, jsonify

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from humanfriendly import format_timespan
from typing import Tuple

from dataclasses import dataclass
from datetime import datetime, timedelta

from data import Articles

from db import Dashboard, SensorData, ModeStatistics

import mysql.connector
import humanfriendly

# ----------------------------------------------------------------------------------------------------------------------

class FusionLink(object):
    _host: str = "83.175.125.85"
    _user: str = "infinity"
    _password: str = "iGe9kH9j"

    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        self.db_link = mysql.connector.connect(host=FusionLink._host,
                                               user=FusionLink._user,
                                               password=FusionLink._password)

    # ------------------------------------------------------------------------------------------------------------------

    def query(self, sql: str):
        cursor = self.db_link.cursor(buffered=True)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

# ----------------------------------------------------------------------------------------------------------------------


database = FusionLink()


sql = "SELECT info.uk_device_sn, info.device_mode_ind, info.last_update_dtm FROM bbf_inf_rep.DeviceInfo info;"
def example_query(sql):
    db_result = database.query(sql)
    return db_result

# ----------------------------------------------------------------------------------------------------------------------

app = Flask(__name__)

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

Articles = Articles()

# ----------------------------------------------------------------------------------------------------------------------

@app.route('/')
def index():
    dash = Dashboard()
    start_date = datetime.now() - timedelta(days=7)
    dashboard = dash.dashboard(start_date)
    return render_template('home.html', dashboard=dashboard)

# ----------------------------------------------------------------------------------------------------------------------

@app.route('/statistics/mode')
def statistics_mode():
    data = ModeStatistics().mode_counts()
    #start_date = datetime.now() - timedelta(days=7)
    labels=["Auto", "Off", "Manual", "Light Shower"]
    return render_template('statistics_mode.html', data=data, labels=jsonify(labels))

# ----------------------------------------------------------------------------------------------------------------------

@app.route('/sensors')
def sensors():
    sensor_data = SensorData().current_sensor_data()

    return render_template('sensors.html', sensors=sensor_data)

# ----------------------------------------------------------------------------------------------------------------------

def time_series_plot(x, y, x_range):
    if len(x) == 0:
        return "", ""
    fig = figure(plot_width=800, plot_height=150, x_range=x_range, x_axis_type='datetime', toolbar_location=None)
    #fig.sizing_mode = 'scale_width'
    fig.line(
        x=x,
        line_width=1,
        y=y,
        line_color='navy'
    )

    # render template
    script, div = components(fig)
    return script, div

# ----------------------------------------------------------------------------------------------------------------------


def create_timeseries(sensor_data, sensor: str, unit: str, time_range: Tuple[datetime, datetime]):
    start_date, end_date = time_range
    plot_scripts = {}
    plot_divs = {}
    for device, data in sensor_data.items():
        script, div = time_series_plot(data.timestamp, data[[sensor.lower()]].iloc[:, 0],
                                       x_range=(start_date, end_date))
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


@app.route('/sensors/temperature')
def sensors_temp():
    now = datetime.now()
    start_date = now - timedelta(days=2)
    sensor_data = SensorData().temperature(start_date)

    return create_timeseries(sensor_data, sensor="Temperature", unit="°C", time_range=(start_date, now))

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/sensors/brightness')
def sensors_brightness():
    now = datetime.now()
    start_date = now - timedelta(days=2)
    sensor_data = SensorData().brightness(start_date)

    return create_timeseries(sensor_data, sensor="Brightness", unit="lx", time_range=(start_date, now))

# ----------------------------------------------------------------------------------------------------------------------

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


@app.route('/articles')
def articles():
    return render_template('articles.html', articles = Articles)

@app.route('/bokeh')
def bokeh():

    # init a basic bar chart:
    # http://bokeh.pydata.org/en/latest/docs/user_guide/plotting.html#bars
    fig = figure(plot_width=600, plot_height=600)
    fig.line(
        x=[1, 2, 3, 4],
        line_width=1,
        y=[1.7, 2.2, 4.6, 3.9],
        line_color='navy'
    )

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(fig)
    html = render_template(
        'bokeh.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
    )
    return encode_utf8(html)

# ----------------------------------------------------------------------------------------------------------------------

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id)

# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)