from datetime import datetime

# ----------------------------------------------------------------------------------------------------------------------


def parse_date(timestamp):
    if isinstance(timestamp, datetime):
        return timestamp
    try:
        return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.strptime(timestamp, '%Y-%m-%d %H:%M')

# ----------------------------------------------------------------------------------------------------------------------


def format_time_span(input):
    seconds = input.seconds
    minutes = seconds // 60
    seconds = seconds % 60
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# ----------------------------------------------------------------------------------------------------------------------
