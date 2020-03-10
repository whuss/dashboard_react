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
