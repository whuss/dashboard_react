import re
import os
from flask import url_for
from utils.date import parse_date
from datetime import timedelta

from db import Errors

# ----------------------------------------------------------------------------------------------------------------------


TRACE_RE = re.compile(r"(.*) \[(.+):(\d+)\]")

# ----------------------------------------------------------------------------------------------------------------------


def format_logentry(lp, device=None):
    # This is obsolete, and only needed for old log entries
    # Trace log entries get correctly formatted since commit a30b3b5e2afc1b5a7c5790e0f53596cf8c9f80d4
    if lp.log_level == "TRACE":
        match = TRACE_RE.match(lp.message)
        if match:
            lp.message = match.group(1)
            lp.filename = match.group(2)
            lp.line_number = int(match.group(3))

    filename = os.path.basename(lp.filename)
    location = f"[{filename}:{lp.line_number}]:"
    time = lp.timestamp.strftime('%Y-%m-%d %H:%M:%S')

    if filename == "watchdog.py" and lp.log_level == "INFO":
        log_level_class = "WATCHDOG_INFO"
    else:
        log_level_class = lp.log_level

    if device:
        log_url = url_for('show_logs', device=device, duration=1, log_level="TRACE", timestamp=time)
        time_format = f'<a href="{log_url}">{time}</a>'
    else:
        time_format = time

    header_no_format = f'({time}) {lp.log_level:<8} {location:>25} '
    header = f'({time_format}) <span class="{log_level_class}">{lp.log_level:<8}</span> ' \
             f'<span class="log-filename" data-toggle="tooltip" title="{lp.filename}:{lp.line_number}" >' \
             f'{location:>25}</span> '
    indentation = len(header_no_format) * " "
    message_lines = lp.message.split("\n")
    formatted_message = header + message_lines[0] + "\n" + \
        "\n".join([indentation + line for line in message_lines[1:]])

    if len(message_lines) > 1:
        formatted_message += "\n"

    return formatted_message


# ----------------------------------------------------------------------------------------------------------------------


def format_logs(logs, device=None):
    log_text = ""
    for index, lp in logs.iterrows():
        log_text += format_logentry(lp, device)

    return log_text


# ----------------------------------------------------------------------------------------------------------------------


def fetch_logs(device_id, timestamp, log_level="TRACE", before=2, after=2, page=None, filename=None, line_number=None):
    restart_time = parse_date(timestamp)
    start_date = restart_time - timedelta(minutes=before)
    end_date = restart_time + timedelta(minutes=after)

    logs, pagination = Errors().logs(device_id=device_id, log_level=log_level, since=start_date, until=end_date,
                                     page=page, filename=filename, line_number=line_number)
    if not logs.empty:
        log_text = format_logs(logs, device=device_id)
    else:
        log_text = "No logs available."
    return log_text, pagination

# ----------------------------------------------------------------------------------------------------------------------
