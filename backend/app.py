import logging
from datetime import datetime, timedelta
from logging.config import dictConfig
from typing import Tuple

import coloredlogs
import dateutil.parser
from flask import Flask, jsonify, request, json, Response
from flask_caching import Cache
from flask_cors import CORS, cross_origin
# from flask_basicauth import BasicAuth
from flask_table import Col

from ajax_plots import AjaxFactory, PlotDatabaseSize
from ajax_plots import TableRestarts
from config import Config
from db import Errors, Dashboard
from db import db
from db import get_devices
from logs import fetch_logs
from utils.excel import convert_to_excel

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
    app.config['CACHE_TYPE'] = "filesystem"
    app.config['CACHE_DIR'] = Config.cache_dir
    app.config['CACHE_DEFAULT_TIMEOUT'] = 60 * 60 * 23 + 60 * 30  # 23 hours and 30 minutes
    app.config['CACHE_REDIS_HOST'] = "127.0.0.1"
    app.config['CACHE_REDIS_PORT'] = 6379
    app.config['CACHE_THRESHOLD'] = 10000
    db.init_app(app)

    # basic_auth = BasicAuth(app)
    return app

# ----------------------------------------------------------------------------------------------------------------------


app = create_app()
# secret_key is needed for POST requests to gunicorn (otherwise we get error code 500 on post methods)
app.secret_key = "ddm,n.490fsdfgjlk34rdflöja3sdfsaderoivnsdfsadr2430ß56200".encode('utf8')
cache = Cache(app)
cors = CORS(app, resources={r"/backend/*": {"origins": "*"}})
app.app_context().push()
db.Model.metadata.reflect(bind=db.engine)

# ----------------------------------------------------------------------------------------------------------------------<
# Routes
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
# Backend
# ----------------------------------------------------------------------------------------------------------------------


@app.route('/backend/devices')
def backend_devices():
    return jsonify(get_devices())

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/backend/device_state/<device>')
@cache.cached(timeout=60)
def backend_device_state(device: str):
    data = Dashboard.info(device)

    return dict(device=device,
                study_mode=data['study_mode'],
                offline_duration=data['offline_duration'],
                health_status=data['health_status'],
                sick_reason=data['sick_reason'])

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/backend/test_plot')
def backend_test_plot():
    from plots import test_plot
    from bokeh.embed import json_item
    plot = test_plot()
    return json.dumps(json_item(plot, 'testplot'))

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/backend/plot_database_size')
def backend_plot_database_size():
    from ajax_plots import reactify_bokeh
    ajax = PlotDatabaseSize(plot_parameters=dict())

    data = ajax.fetch_data()
    if data.empty:
        return dict()

    plot = ajax._plot(data)
    return reactify_bokeh(plot)

# ----------------------------------------------------------------------------------------------------------------------


@cache.memoize()
def fetch_data(plot_name: str, plot_parameters):
    logging.info(f"fetch render data: {plot_name}, {plot_parameters}")
    ajax = AjaxFactory._create_plot(plot_name, plot_parameters)
    data = ajax.fetch_data()
    return data

# ----------------------------------------------------------------------------------------------------------------------


@cache.memoize()
def react_render(plot_name: str, plot_parameters):
    data = fetch_data(plot_name, plot_parameters)
    logging.info(f"render plot: {plot_name}, {plot_parameters}")
    ajax = AjaxFactory._create_plot(plot_name, plot_parameters)
    return ajax.react_render(data)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/backend/plot/<plot_name>', methods=['POST'])
def backend_plot(plot_name: str):
    try:
        plot_parameters = request.get_json()
        logging.info(f"Plot Cached: plot_name: {plot_name} plot_parameters: {plot_parameters}")
        return react_render(plot_name, plot_parameters)
    except Exception:
        import traceback
        tb = traceback.format_exc()
        logging.error(f"plot_name={plot_name}, plot_parameters={plot_parameters}\n{tb}")
        return dict(error=tb, plot_parameters=plot_parameters, plot_name=plot_name)


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/backend/plot_uncached/<plot_name>', methods=['POST'])
def backend_plot_uncached(plot_name: str):
    try:
        plot_parameters = request.get_json()
        logging.info(f"Plot Uncached: plot_name: {plot_name} plot_parameters: {plot_parameters}")
        ajax = AjaxFactory._create_plot(plot_name, plot_parameters)
        return ajax.react_render()
    except Exception:
        import traceback
        tb = traceback.format_exc()
        logging.error(f"plot_name={plot_name}, plot_parameters={plot_parameters}\n{tb}")
        return dict(error=tb, plot_parameters=plot_parameters, plot_name=plot_name)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/backend/download_excel/<plot_name>', methods=['POST'])
def backend_download_excel(plot_name: str):
    plot_parameters = request.get_json()
    logging.info(f"plot_name: {plot_name} plot_parameters: {plot_parameters}")
    plot = AjaxFactory._create_plot(plot_name, plot_parameters)
    data = plot.fetch_data()
    return Response(convert_to_excel(data),
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-disposition":
                             "attachment; filename=data.xlsx"})

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/backend/system_restarts/<device>')
def backend_system_restarts(device: str):
    data, pagination = Errors.restarts(device, limit=10, page=1)
    data.timestamp = data.timestamp.astype(str)
    data.version_timestamp = data.version_timestamp.astype(str)
    return dict(table=data.to_dict(orient='records'))

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/logs/<device>', methods=['GET'])
@app.route('/logs/<device>/<int:duration>', methods=['GET'])
@app.route('/logs/<device>/<int:duration>/<log_level>', methods=['GET'])
@app.route('/logs/<device>/<int:duration>/<log_level>/<timestamp>/', methods=['GET'])
def show_logs(device, duration=5, timestamp=None, log_level="TRACE"):
    """Dummy route, only used to build links, that are handled by the frontend."""
    return ""

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/backend/logs/<device>', methods=['GET'])
@app.route('/backend/logs/<device>/<int:duration>', methods=['GET'])
@app.route('/backend/logs/<device>/<int:duration>/<log_level>', methods=['GET'])
@app.route('/backend/logs/<device>/<int:duration>/<log_level>/<timestamp>/', methods=['GET'])
@cross_origin()
def backend_logs(device, duration=5, timestamp=None, log_level="TRACE"):
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
    return dict(devices=devices,
                log_text=log_text,
                device=device,
                pagination=dict(has_prev=pagination.has_prev,
                                prev_num=pagination.prev_num,
                                current_page=page,
                                num_pages=pagination.pages,
                                pages=list(pagination.iter_pages()),
                                has_next=pagination.has_next,
                                next_num=pagination.next_num
                                ))

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/backend/settings/<device>')
def backend_settings(device: str):
    from analytics.settings import get_settings
    return jsonify(get_settings(device))

# ----------------------------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=Config.debug)

# ----------------------------------------------------------------------------------------------------------------------
