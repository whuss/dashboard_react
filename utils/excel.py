import pandas as pd
from datetime import date, time, timedelta, datetime
from tempfile import mkstemp
import xlsxwriter
import os

# ----------------------------------------------------------------------------------------------------------------------

# TODO: remove tempfile:
# from io import BytesIO
#
# output = BytesIO()
# workbook = xlsxwriter.Workbook(output)
# worksheet = workbook.add_worksheet()
#
# worksheet.write('A1', 'Hello')
# workbook.close()
#
# xlsx_data = output.getvalue()

# ----------------------------------------------------------------------------------------------------------------------

def int_to_alpha(x: int) -> str:
    if x >= 26:
        raise NotImplementedError("Column names bigger than Z are not implemented.")
    return chr(x + ord('A'))

# ----------------------------------------------------------------------------------------------------------------------


def cell(row: int, column: int) -> str:
    return f"{int_to_alpha(column)}{row+1}"

# ----------------------------------------------------------------------------------------------------------------------


def dataframe_to_excel(data: pd.DataFrame, filename: str) -> None:
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()

    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
    datetime_format = workbook.add_format({'num_format': 'yyy-mm-dd hh:mm:ss'})
    time_format = workbook.add_format({'num_format': 'hh:mm:ss'})
    timedelta_format = workbook.add_format({'num_format': '[hh]:mm:ss'})

    excel_format_dict = dict(date=date_format,
                             datetime=datetime_format,
                             timedelta=timedelta_format)

    def excel_format_(value, column_name: str):
        c = data[column_name]
        if pd.api.types.is_timedelta64_dtype(c):
            return timedelta_format
        if pd.api.types.is_datetime64_dtype(c):
            return datetime_format
        if isinstance(value, date):
            return date_format

    def excel_format(value):
        if isinstance(value, timedelta):
            return timedelta_format
        if isinstance(value, datetime):
            return datetime_format
        if isinstance(value, time):
            return time_format
        if isinstance(value, date):
            return date_format
        return None

    columns = data.columns

    for c_index, header in enumerate(columns):
        worksheet.write(cell(0, c_index+1), header)
    for r_index, (index, row) in enumerate(data.iterrows()):
        worksheet.write(cell(r_index+1, 0), index, excel_format(index))
        for c_index, c_name in enumerate(columns):
            entry = row[c_name]
            worksheet.write(cell(r_index+1, c_index+1), entry, excel_format(entry))
    workbook.close()

# ----------------------------------------------------------------------------------------------------------------------


def convert_to_excel(data: pd.DataFrame) -> bytes:
    #with NamedTemporaryFile() as temp_file:
    _, temp_file = mkstemp(suffix="xlsx")
    try:
        dataframe_to_excel(data, temp_file)
        with open(temp_file, 'r+b') as file_read:
            content = file_read.read()
    finally:
        os.remove(temp_file)

    return content

# ----------------------------------------------------------------------------------------------------------------------
