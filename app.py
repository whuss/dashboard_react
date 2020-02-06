# Video: https://www.youtube.com/watch?v=zRwy8gtgJ1A
# Code from: https://github.com/bradtraversy/myflaskapp

from flask import Flask, render_template
from dataclasses import dataclass

from data import Articles

import mysql.connector

class FusionLink(object):
    _host: str = "83.175.125.85"
    _user: str = "infinity"
    _password: str = "iGe9kH9j"

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        self.db_link = mysql.connector.connect(host=FusionLink._host,
                                               user=FusionLink._user,
                                               password=FusionLink._password)

    # -----------------------------------------------------------------------------------------------------------------

    def query(self, sql: str):
        cursor = self.db_link.cursor(buffered=True)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

# ---------------------------------------------------------------------------------------------------------------------


db = FusionLink()

dashboard_sql_query = """SELECT info.uk_device_sn, info.device_mode_ind, info.last_update_dtm, mode.ix_mode_ind,
       CONCAT(LPAD(HOUR(TIMEDIFF(now(), mode.ix_data_dtm)), 2, '0'), ':', LPAD(MINUTE(TIMEDIFF(now(), mode.ix_data_dtm)), 2, '0'), ':', LPAD(SECOND(TIMEDIFF(now(), mode.ix_data_dtm)), 2, '0')) as since,
       light.light_count, mouse.mouse_count
FROM
bbf_inf_rep.DeviceInfo info
LEFT JOIN
(SELECT sub1.ix_device_sn as ix_device_sn, sub1.ix_data_dtm as ix_data_dtm, sub1.ix_mode_ind as ix_mode_ind
FROM bbf_inf_rep.LightingPackage sub1
JOIN (SELECT ix_device_sn, ix_data_dtm, MAX(pk_lighting_package_id) as lastone
FROM bbf_inf_rep.LightingPackage
GROUP BY ix_device_sn) sub2 on sub1.pk_lighting_package_id = sub2.lastone) as mode
ON info.uk_device_sn = mode.ix_device_sn
LEFT JOIN
(SELECT ix_device_sn, COUNT(*) AS mouse_count
FROM bbf_inf_rep.MouseGesturePackage
WHERE ix_data_dtm>='2020-01-01 00:00:00'
GROUP BY ix_device_sn) as mouse
ON info.uk_device_sn = mouse.ix_device_sn
LEFT JOIN
(SELECT ix_device_sn, COUNT(*) AS light_count
FROM bbf_inf_rep.LightingPackage
WHERE ix_data_dtm>='2020-01-01 00:00:00'
GROUP BY ix_device_sn) as light
ON info.uk_device_sn = light.ix_device_sn;
"""

keys = ["uk_device_sn", "device_mode_ind", "last_update_dtm", "ix_mode_ind", "since", "light_count", "mouse_count"]

app = Flask(__name__)

# ---------------------------------------------------------------------------------------------------------------------

Articles = Articles()

# ---------------------------------------------------------------------------------------------------------------------

@app.route('/')
def index():
    #sql = "SELECT info.uk_device_sn, info.device_mode_ind, info.last_update_dtm FROM bbf_inf_rep.DeviceInfo info;"
    db_result = db.query(dashboard_sql_query)
    db_result = [dict(zip(keys, row)) for row in db_result]

    return render_template('home.html', dashboard=db_result)

# ---------------------------------------------------------------------------------------------------------------------

@app.route('/about')
def about():
    return render_template('about.html')

# ---------------------------------------------------------------------------------------------------------------------

@app.route('/articles')
def articles():
    return render_template('articles.html', articles = Articles)

# ---------------------------------------------------------------------------------------------------------------------

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id)

# ---------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)