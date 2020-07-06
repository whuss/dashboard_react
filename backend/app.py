import logging
from datetime import datetime, timedelta
from logging.config import dictConfig
from typing import Tuple

import coloredlogs
import dateutil.parser
from flask import Flask, jsonify, request, json, Response
from flask_caching import Cache
from flask_cors import CORS, cross_origin

from ajax_plots import AjaxFactory
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

# ----------------------------------------------------------------------------------------------------------------------
# Backend Routes
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
# Example route
# ----------------------------------------------------------------------------------------------------------------------

@app.route('/backend/chart_data')
def chart_data():
    from time import sleep
    # simulate database response time
    sleep(2)
    return dict(monitor=[0, 59, 12, 81, 56, 0], paper=[0, 81, 56, 55, 95, 0])


# ----------------------------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=Config.debug)

# ----------------------------------------------------------------------------------------------------------------------
