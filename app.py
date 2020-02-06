# Video: https://www.youtube.com/watch?v=zRwy8gtgJ1A
# Code from: https://github.com/bradtraversy/myflaskapp

from flask import Flask, render_template
from dataclasses import dataclass
from datetime import datetime, timedelta

from data import Articles

from db import Dashboard

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
        return input if input else ""

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

    return dict(_str=_str,
                _time_span=_time_span,
                _number=_number)

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

def index_old():


    return render_template('home.html', dashboard=db_result)

# ----------------------------------------------------------------------------------------------------------------------

@app.route('/about')
def about():
    return render_template('about.html')

# ----------------------------------------------------------------------------------------------------------------------

@app.route('/articles')
def articles():
    return render_template('articles.html', articles = Articles)

# ----------------------------------------------------------------------------------------------------------------------

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id)

# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)