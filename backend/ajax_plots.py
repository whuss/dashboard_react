import hashlib
import hmac
import io
import logging
import os
import pickle
import threading
import traceback
from abc import abstractmethod
from base64 import b64encode, b64decode
from datetime import timedelta, date
from typing import Dict

import numpy as np
import pandas as pd
from bokeh.embed import components
from bokeh.layouts import column
from flask import jsonify
from flask_table import Col, LinkCol, Table
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure

# ----------------------------------------------------------------------------------------------------------------------


plot_lock = threading.Lock()

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

    def json(self):
        return self._value

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


class AjaxFieldTable(AjaxField):
    def __init__(self, name: str):
        super().__init__(name)
        self.initial_value = "Loading Table ..."

    # ------------------------------------------------------------------------------------------------------------------

    def set_value(self, value):
        self._value = value

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def final_html(self):
        if self._value is None:
            return "no data"

        return self._value.__html__()

    # ------------------------------------------------------------------------------------------------------------------

    def json(self):
        if self._value is None:
            return ""
        else:
            return self._value.__html__()

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


class AjaxFieldPlotBokeh(AjaxField):
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
            self._final_html = f"{div}\n{script}"

    # ------------------------------------------------------------------------------------------------------------------

    def json(self):
        return ""

# ----------------------------------------------------------------------------------------------------------------------


class AjaxFieldPlotMplPng(AjaxField):
    def __init__(self, name: str):
        super().__init__(name)
        self.initial_value = "Loading plot ..."

    # ------------------------------------------------------------------------------------------------------------------

    def set_value(self, value):
        self._value = value

        if self._value is None:
            self._final_html = f"no data"
        else:
            output = io.BytesIO()
            FigureCanvasAgg(self._value).print_png(output)
            plot_data = b64encode(output.getvalue()).decode('ascii')

            self._final_html = f'<img src="data:image/png;charset=US-ASCII;base64,{plot_data}">'

# ----------------------------------------------------------------------------------------------------------------------


class AjaxFieldPlotMplSvg(AjaxField):
    def __init__(self, name: str):
        super().__init__(name)
        self.initial_value = "Loading plot ..."

    # ------------------------------------------------------------------------------------------------------------------

    def set_value(self, value):
        self._value = value

        if self._value is None:
            self._final_html = f"no data"
        else:
            output = io.BytesIO()
            FigureCanvasSVG(self._value).print_svg(output)
            plot_data = b64encode(output.getvalue()).decode('ascii')

            self._final_html = f'<img src="data:image/svg+xml;charset=US-ASCII;base64,{plot_data}">'

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

def reactify_bokeh(plot):
    script, div = components(plot)

    script = script.replace('\n<script type=\"text/javascript\">', '') \
        .replace('\n</script>', '')

    div_ = "{" + div.replace('\n<div ', '') \
        .replace('></div>', '') \
        .replace(' ', ',') \
        .replace('data-root-id=', '"data_root_id":') \
        .replace('id=', '"id":') \
        .replace('class=', '"class":') + "}"

    print(div_)

    from ast import literal_eval
    data = literal_eval(div_)
    print(data)
    data['script'] = script
    data['div'] = div

    return data

# ----------------------------------------------------------------------------------------------------------------------

class AjaxPlotBokeh(Ajax):
    def __init__(self, plot_parameters: dict):
        super().__init__(plot_parameters)
        self.add_field(AjaxFieldPlotBokeh(name='plot'))
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

    # ------------------------------------------------------------------------------------------------------------------

    def react_render(self, data=None):
        if data is None:
            data = self.fetch_data()
        if data is None or data.empty:
            return dict()

        plot = self._plot(data)
        json_plot = reactify_bokeh(plot)
        json_fields = dict()
        for name, field in self.field.items():
            json_fields[name] = field.json()
        return dict(plot=json_plot, fields=json_fields)

# ----------------------------------------------------------------------------------------------------------------------


def reactify_mpl(plot):
    output = io.BytesIO()
    plot.savefig(output, format="png")
    json = dict(png=b64encode(output.getbuffer()).decode('ascii'))
    plot.clf()
    return json

# ----------------------------------------------------------------------------------------------------------------------


class AjaxPlotMpl(Ajax):
    def __init__(self, plot_parameters: dict):
        super().__init__(plot_parameters)
        self.add_field(AjaxFieldPlotMplPng(name='plot'))
        #self.add_field(AjaxFieldPlotMplSvg(name='plot_svg'))
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
        # self.field['plot_svg'].set_value(plot)

    # ------------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def _fetch(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def _plot(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------

    def react_render(self, data=None):
        if data is None:
            data = self.fetch_data()
        if data is None or data.empty:
            return dict()

        with plot_lock:
            plot = self._plot(data)
            json_plot = reactify_mpl(plot)
        json_fields = dict()
        for name, field in self.field.items():
            json_fields[name] = field.json()
        return dict(plot=json_plot, fields=json_fields)

# ----------------------------------------------------------------------------------------------------------------------
# Example Plots
# ----------------------------------------------------------------------------------------------------------------------


class PlotExampleBokeh(AjaxPlotBokeh):
    def __init__(self, plot_parameters: dict):
        super().__init__(plot_parameters)
        self.number_of_points = plot_parameters.get('number_of_points', 100)

    # ------------------------------------------------------------------------------------------------------------------

    def _fetch(self):
        import numpy as np
        # create three normal population samples with different parameters
        x = np.array(range(self.number_of_points))
        y = np.sin(x/10)
        data = pd.DataFrame(np.vstack([x,y]).T, columns=['x', 'y'])
        if data.empty:
            return None

        return data

    # ------------------------------------------------------------------------------------------------------------------

    def _plot(self, data):
        x = data.x
        y = data.y
        from bokeh.plotting import figure

        p = figure(title="simple line example", x_axis_label='x', y_axis_label='y')

        # add a line renderer with legend and line thickness
        p.line(x, y, legend_label="sin(x/10)", line_width=2)
        return p

# ----------------------------------------------------------------------------------------------------------------------


class PlotExampleMatplotlib(AjaxPlotMpl):
    def __init__(self, plot_parameters: dict):
        super().__init__(plot_parameters)
        self.sigma = plot_parameters.get('sigma', 15)  # standard deviation of distribution
        self.mu = plot_parameters.get('mu', 100)


    # ------------------------------------------------------------------------------------------------------------------

    def _fetch(self):
        # example data
        x = self.mu + self.sigma * np.random.randn(437)

        data = pd.DataFrame(x, columns=['x'])
        if data.empty:
            return None

        return data

    # ------------------------------------------------------------------------------------------------------------------

    def _plot(self, data):
        x = data.x
        import matplotlib.pyplot as plt

        # the histogram of the data
        num_bins = 50
        fig, ax = plt.subplots()
        n, bins, patches = ax.hist(x, num_bins, density=1)

        y = ((1 / (np.sqrt(2 * np.pi) * self.sigma)) *
                np.exp(-0.5 * (1 / self.sigma * (bins - self.mu))**2))

        # add a 'best fit' line

        ax.plot(bins, y, '--')
        ax.set_xlabel('Smarts')
        ax.set_ylabel('Probability density')
        ax.set_title(f'Histogram of IQ: $\\mu={self.mu}$, $\\sigma={self.sigma}$')

        # Tweak spacing to prevent clipping of ylabel
        fig.tight_layout()
        return fig

# ----------------------------------------------------------------------------------------------------------------------