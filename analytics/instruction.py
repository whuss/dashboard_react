from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from dataclasses import dataclass

from db import db, InstructionPackage, VersionPackage
from utils.interval import TimeInterval, Interval, parse_interval
from utils.date import start_of_day, end_of_day
from datetime import date

# ----------------------------------------------------------------------------------------------------------------------


def get_instructions_data(device: str, interval) -> pd.DataFrame:
    """Returns dataframe of all instructions that changed the ptl running mode in the given interval.

    @parameter: device
        Device name of a PTL

    @parameter: interval
        A time interval. Either a tuple of two date objects, or an object with properties 'begin' and 'end'
        which return date objects.

    @returns: a pandas dataframe with data columns 'target' and 'status'.

        target: contains strings in the set {'POWER_PRESENCE', 'POWER_MANUAL', 'LIGHT_SHOWER',
                                             'TASK_VERT', 'TASK_HORI', 'SETTINGS', 'RESTART'}
        status: contains strings in the set {'OFF', 'ON'}

        The dataframe is sorted by its datetime index column named timestamp.
    """

    interval = parse_interval(interval)
    since, until = interval.begin, interval.end

    # Gather instructions
    ip = InstructionPackage

    # Find the timestamp of the last instruction before the selected time interval
    query_last_timestamp = db.session.query(db.func.max(ip.timestamp).label('timestamp')) \
        .filter(ip.instruction == "MODE") \
        .filter(ip.device == device) \
        .filter(ip.timestamp < since)

    sq_last_timestamp = query_last_timestamp.subquery()

    # Get the last recorded sensor value before the selected time interval
    query_last_mode = db.session.query(ip.source, ip.target, ip.value) \
        .filter(ip.device == device) \
        .filter(ip.timestamp == sq_last_timestamp.c.timestamp)

    first_mode = query_last_mode.first()

    # Get instruction values in the selected time interval
    query = db.session.query(ip.source, ip.target, ip.value, ip.timestamp) \
        .filter(ip.instruction == "MODE") \
        .filter(ip.device == device) \
        .filter(ip.timestamp >= since) \
        .filter(ip.timestamp <= until) \
        .order_by(ip.timestamp)

    # Create data frame
    if first_mode:
        data_since = pd.DataFrame({"timestamp": [since],
                                   "source": first_mode.source,
                                   "target": first_mode.target,
                                   "value": first_mode.value})
    else:
        data_since = pd.DataFrame()
    data_between = pd.DataFrame(query.all())

    data_instructions = pd.concat([data_since, data_between], axis=0) \
        .rename(columns=dict(value="status"))

    if not data_instructions.empty:
        # Remove "None@" from column source
        def format_source(source):
            try:
                return source.split("@")[1]
            except IndexError:
                return source

        data_instructions.source = data_instructions.source.apply(format_source)

        # Distinguish between manual power commands and power commands based on presence detection.
        def power(row):
            if row['target'] == "POWER":
                if row['source'] == "Lullaby":
                    return "POWER_PRESENCE"
                if row['source'] == "DataDock":
                    return "POWER_MANUAL"

                raise ValueError(f"Unknown combination of source={row['source']} and target={row['target']}.")

            return row['target']

        data_instructions.target = data_instructions.apply(power, axis=1)

        # select columns
        data_instructions = data_instructions[['timestamp', 'target', 'status']]

    # find all restarts in the selected time interval
    vp = VersionPackage
    query_restart = db.session.query(vp.timestamp) \
        .filter(vp.device == device) \
        .filter(vp.timestamp >= since) \
        .filter(vp.timestamp <= until) \
        .order_by(vp.timestamp)

    data_restart = pd.DataFrame(query_restart.all())
    data_restart['target'] = "RESTART"
    data_restart['status'] = "ON"

    # combine instructions and restarts
    data = pd.concat([data_instructions, data_restart], axis=0)

    # sort and set index
    if not data.empty:
        data = data.sort_values(by="timestamp").set_index("timestamp")
        data.index.name = "timestamp"

    return data

# ----------------------------------------------------------------------------------------------------------------------


@dataclass
class PtlState:
    """Encodes all possible states of the PTL, that are tracked for data analysis.

    The state is encoded as a 3 tuple (power, scene, settings) where each component
    is an element in a set of finite strings.

    power: in {'OFF', 'ON'}, describing if the PTL is turned on or off.
    scene: in {'AUTO', 'TASK_HORI', 'TASK_VERT', 'LIGHT_SHOWER'} describing the
        selected lighting scene, where 'AUTO' corresponds to the AI-controlled mode.
    settings: in {'OFF', 'ON'}, describing if the settings panel is open
        on the PTL windows control application.

    Note: This represenation is choosen over Enum, because it makes it easier to store
        states in in pandas dataframes.
    """
    power: str
    scene: str
    settings: str

# ----------------------------------------------------------------------------------------------------------------------


def state_transitions(state: PtlState, instruction) -> PtlState:
    """Transition function mapping a PTL 'state' to a new PTL state according
    to 'instruction' which is tuple representation of the known PTL instructions.

    @parameter: state
        Represents the current state of the PTL

    @parameter: instruction:
        Represents an instruction that is applied to the current state.

        'instruction' has string properties 'target' and 'status' with values in the sets:

        instruction.target in {'POWER_PRESENCE', 'POWER_MANUAL', 'LIGHT_SHOWER',
                               'TASK_VERT', 'TASK_HORI', 'SETTINGS', 'RESTART'}
        instruction.status in {'OFF', 'ON'}

        Note: The parameter 'instruction' has the same format as the data rows returned by
              the get_instructions_data() function.

    @returns: a new PtlState that is the result of applying instruction to state.

    Note: The transition are defined according to the table defined in doc/state_transitions.ods

    Note: The transitions function contains all possible combinations of (state, instruction) pairs,
          also some that cannot happen in the real PTL. Since there is the possibility that some
          instructions are not recorded in the database (loss of internet connection, etc.), we cannot
          assume that only transitions that happen in the actual PTL happen, when the state_transition
          function is applied to a list of instructions that are downloaded from the database.
    """
    new_state: PtlState = PtlState(state.power, state.scene, state.settings)
    if instruction.target in ["POWER_PRESENCE", "POWER_MANUAL"]:
        new_state.power = instruction.status
        return new_state

    if instruction.target in ["LIGHT_SHOWER", "TASK_HORI", "TASK_VERT"]:
        new_state.power = "ON"
        new_state.settings = "OFF"
        if instruction.status == "ON":
            new_state.scene = instruction.target
        elif instruction.status == "OFF":
            new_state.scene = "AUTO"
        else:
            raise ValueError(f"Unknown transition: state={(state.power, state.scene, state.settings)}, "
                             f"transition={(instruction.target, instruction.value)}")
        return new_state

    if instruction.target == "SETTINGS":
        new_state.settings = instruction.status
        return new_state

    if instruction.target == "RESTART":
        new_state.scene = "AUTO"
        new_state.settings = "OFF"
        return new_state

    raise ValueError(f"Unknown transition: state={(state.power, state.scene, state.settings)}, "
                     f"transition={(instruction.target, instruction.value)}")

# ----------------------------------------------------------------------------------------------------------------------


def get_state_data(device: str, interval, resample_rule: Optional[str] = None) -> pd.DataFrame:
    """Calculate PTL states for the selected time interval.

    Since the PTL does not actually record its state in the database, (and actually does not even track its state
    internally) we need to compute its state from the instructions that are recorded in the database
    InstructionPackage table. The instructions are downloaded by the get_instructions_data() function in this module.

    The state of the PTL is encoded by the PtlState class. Note the get_instructions_data() function does not return
    object of type PtlState but each data row is a pandas series item with the same format as PtlState, and thus can
    be used in place of PtlState.

    @parameter: device
        Device name of a PTL

    @parameter: interval
        A time interval. Either a tuple of two date objects, or an object with properties 'begin' and 'end'
        which return date objects.

    @parameter: resample_rule
        When resample_rule is given, the returned dataframe is resampled with the selected rule. The format
        of this parameter is the same as the rule parameter of the pandas resample function, i.e. use '1S' to
        get a data point every second. The state of a timestamp is extrapolated from the last known state,
        it is assumed that no unknown state changes occurred.

        The last known state is extended until the end of the selected time interval.

        Note: It is not checked if the end of the time interval lies in the future.

    @returns: a pandas dataframe with data columns 'power' and 'scene' and 'settings' describing the state of the PTL.

        power: contains strings in the set {'OFF', 'ON'}, describing if the PTL is turned on or off.
        scene: contains strings in the set {'AUTO', 'TASK_HORI', 'TASK_VERT', 'LIGHT_SHOWER'} describing the
            selected lighting scene, where 'AUTO' corresponds to the AI-controlled mode.
        settings: contains strings in the set {'OFF', 'ON'}, describing if the settings panel is open
            on the PTL windows control application.

        The dataframe is sorted by its datetime index column named timestamp.
    """
    data = get_instructions_data(device, interval)
    if data.empty:
        empty_data = pd.DataFrame(columns=['power', 'scene', 'settings'])
        empty_data.index.name = "timestamp"
        return empty_data

    interval = parse_interval(interval)
    since, until = interval.begin, interval.end

    data['power'] = pd.NaT
    data['scene'] = pd.NaT
    data['settings'] = pd.NaT

    # Set initial state
    first_timestamp = data.index.min()
    data.loc[first_timestamp, 'power'] = "OFF"
    data.loc[first_timestamp, 'scene'] = "AUTO"
    data.loc[first_timestamp, 'settings'] = "OFF"

    # Apply state transition automaton
    state = None
    for index, row in data.iterrows():
        if not state:
            # the state is already set for the first row
            state = PtlState(row.power, row.scene, row.settings)
            continue

        # compute state transition
        transition = row
        state = state_transitions(state, transition)

        # update state in current row
        row.power = state.power
        row.scene = state.scene
        row.settings = state.settings

    # select only the columns describing the ptl state
    data = data[['power', 'scene', 'settings']]

    if resample_rule:
        # copy the last known PTL state to the end of the selected time interval
        last_ptl_state = data.iloc[-1]
        # only append a data row if the timestamp of the last row is not already the
        # end of the selected time interval
        if last_ptl_state.name != until:
            last_ptl_state.name = until
            data_until = pd.DataFrame([last_ptl_state])
            data = data.append(data_until)

        # resample data
        data = data.resample(resample_rule).ffill().dropna()

        data.index.name = "timestamp"
    return data

# ----------------------------------------------------------------------------------------------------------------------


def get_power(device: str, start_date: date, end_date: Optional[date] = None, resample_rule='1S') -> pd.DataFrame:
    if end_date is None:
        end_date = date.today()
    interval = (start_of_day(start_date), end_of_day(end_date))
    state_data = get_state_data(device, interval, resample_rule='1S')

    state_data.loc[:, 'power'] = (state_data.power == "ON").astype(int)

    power = state_data.drop(columns=["scene", "settings"])

    if power.empty:
        return power

    if resample_rule != "1S":
        power = power.resample(resample_rule).mean()
    return power

# ----------------------------------------------------------------------------------------------------------------------


def plot_power_timeline(data, **kwargs):
    import itertools
    from datetime import timedelta, datetime, date
    from bokeh.core.enums import Dimensions, StepMode
    from bokeh.transform import dodge, cumsum
    from bokeh.plotting import figure
    from bokeh.models import ColumnDataSource, OpenURL, TapTool
    from bokeh.models import WheelZoomTool, ResetTool, BoxZoomTool, HoverTool, PanTool, SaveTool
    from bokeh.models import NumeralTickFormatter, PrintfTickFormatter, Circle
    from bokeh.models.ranges import Range1d
    from bokeh import palettes, layouts
    from bokeh.palettes import Magma256

    from datetime import date
    x_range = kwargs.get('x_range', None)
    if not x_range:
        x_range = (date(2020, 2, 1) - timedelta(days=1), date.today() + timedelta(days=1))

    y_range = 0, 60 * 24  # Minutes of a day

    data['color'] = (data.power * 255).astype(int)
    data['color'] = data.color.apply(lambda c: Magma256[c])

    data_source = ColumnDataSource(data)

    fig = figure(plot_height=500, plot_width=1000,
                 title=f"Power timeline",
                 x_axis_type='datetime',
                 y_axis_type='linear',
                 x_range=x_range,
                 y_range=y_range,
                 tools="")

    fig.rect(y='minutes', x='date', width=timedelta(days=1)/2, height=1, color='orange', source=data_source)

    from datetime import time

    def index_to_time(index: int):
        hours = index // 60
        minutes = index % 60
        if index == 60 * 24:
            return time(0, 0)
        return time(hours, minutes)

    minutes = list(range(0, 60 * 24+1, 3 * 60))
    fig.yaxis.ticker = minutes
    fig.yaxis.major_label_overrides = {m: str(index_to_time(m)) for m in minutes}

    fig.output_backend = "webgl"
    fig.toolbar.logo = None

    hover_tool = HoverTool(tooltips=[('Date', '@date{%F}'),
                                     ('power', '@power')],
                           formatters={'date': 'datetime'})

    fig.add_tools(hover_tool)
    fig.add_tools(SaveTool())
    fig.add_tools(BoxZoomTool())
    fig.add_tools(PanTool())
    fig.add_tools(ResetTool())
    return fig

# ----------------------------------------------------------------------------------------------------------------------
