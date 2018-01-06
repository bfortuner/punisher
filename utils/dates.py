import time
import datetime
import calendar
import dateutil.parser
import pandas as pd
import numpy as np

# https://dateutil.readthedocs.io/en/stable/examples.html

PANDAS_ITERABLE_TYPES = [pd.Series, np.ndarray, pd.DataFrame]

def str_to_date(date_str):
    if date_str is None:
        return date_str

    if type(date_str) in PANDAS_ITERABLE_TYPES:
        if len(date_str) > 0 and date_str[0].isdigit():
            return date_str
        return dateutil.parser.parse(date_str)

    # Leave Epoch Time Alone
    if date_str.isdigit():
        return date_str
    return dateutil.parser.parse(date_str)


def date_to_str(date):
    return date.isoformat() if date is not None else None


def utc_to_epoch(utc_time):
    return calendar.timegm(utc_time.utctimetuple())


def epoch_to_utc(epoch_sec):
    return datetime.datetime.utcfromtimestamp(epoch_sec)


def get_time_range(df, start_utc=None, end_utc=None):
    if start_utc is not None:
        df = df[df.index >= utc_to_epoch(start_utc)]
    if end_utc is not None:
        df = df[df.index < utc_to_epoch(end_utc)]
    return df
