import logging
from logging.config import dictConfig

import coloredlogs
from flask import Flask, jsonify, request, json, Response
from flask_cors import CORS, cross_origin
from db import db
from ajax_plots import AjaxFactory

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
    # If a database is used add the DB connection URL here
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

# ----------------------------------------------------------------------------------------------------------------------


app = create_app()
cors = CORS(app, resources={r"/backend/*": {"origins": "*"}})
app.app_context().push()
db.Model.metadata.reflect(bind=db.engine)

# ----------------------------------------------------------------------------------------------------------------------
# Backend Routes
# ----------------------------------------------------------------------------------------------------------------------


@app.route('/backend/plot/<plot_name>', methods=['POST'])
def backend_plot(plot_name: str):
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
    logging.info(f"fetch render data: {plot_name}, {plot_parameters}")
    ajax = AjaxFactory._create_plot(plot_name, plot_parameters)
    data = ajax.fetch_data()
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
    print("Startup Backend")
    app.run(debug=True)

# ----------------------------------------------------------------------------------------------------------------------
