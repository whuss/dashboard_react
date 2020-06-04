from ast import literal_eval

from db import db, InstructionPackage
from utils.date import format_datetime

# ----------------------------------------------------------------------------------------------------------------------


def parse_settings(settings_str: str):
    settings = literal_eval(settings_str)
    if isinstance(settings, dict):
        return settings

    if isinstance(settings, list):
        vertical_wall_cct = settings[0]
        vertical_wall_intensities = settings[1]
        vertical_table_cct = settings[2]
        vertical_table_intensities = settings[3]

        horizontal_wall_cct = settings[4]
        horizontal_wall_intensities = settings[5]
        horizontal_table_cct = settings[6]
        horizontal_table_intensities = settings[7]

        data = {
            'vertical': {
                'wall': {
                    'cct': vertical_wall_cct,
                    'intensities': vertical_wall_intensities
                },
                'table': {
                    'cct': vertical_table_cct,
                    'intensities': vertical_table_intensities
                }
            },
            'horizontal': {
                'wall': {
                    'cct': horizontal_wall_cct,
                    'intensities': horizontal_wall_intensities
                },
                'table': {
                    'cct': horizontal_table_cct,
                    'intensities': horizontal_table_intensities
                }
            }
        }
        return data

# ----------------------------------------------------------------------------------------------------------------------


def get_settings(device: str):
    ip = InstructionPackage
    query = db.session.query(ip) \
        .filter(ip.device == device) \
        .filter(ip.instruction == "SAVE")
    data = query.all()
    return [dict(timestamp=format_datetime(d.timestamp), settings=parse_settings(d.value)) for d in data]

# ----------------------------------------------------------------------------------------------------------------------
