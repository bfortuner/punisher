import time
import datetime
import calendar
import dateutil.parser
import pandas as pd
import numpy as np
from enum import Enum, unique

# https://dateutil.readthedocs.io/en/stable/examples.html

PANDAS_ITERABLE_TYPES = [pd.Series, np.ndarray, pd.DataFrame]

@unique
class Timeframe(Enum):
    ONE_MIN = {'id': '1m', 'delta': datetime.timedelta(minutes=1)}
    FIVE_MIN = {'id': '5m', 'delta': datetime.timedelta(minutes=5)}
    THIRTY_MIN = {'id': '30m', 'delta': datetime.timedelta(minutes=30)}
    ONE_HOUR = {'id': '1h', 'delta': datetime.timedelta(hours=1)}
    ONE_DAY = {'id': '1d', 'delta': datetime.timedelta(days=1)}

    @property
    def id(self):
        return self.value['id']

    @property
    def delta(self):
        return self.value['delta']

    @classmethod
    def from_id(self, id_):
        '''1m, 5m, 30m'''
        id_map = {e.id:e for e in Timeframe}
        return id_map[id_]


def is_str_digit(string):
    if 'numpy' in type(string).__module__:
        return np.issubdtype(string, np.number)
    return string.isdigit()

def str_to_date(date_str):
    if date_str is None:
        return date_str

    if type(date_str) in PANDAS_ITERABLE_TYPES:
        if len(date_str) > 0 and is_str_digit(date_str[0]):
            return date_str
        return dateutil.parser.parse(date_str)

    # Input is an int
    if type(date_str) is int:
        return date_str

    # Leave Epoch Time Alone
    if is_str_digit(date_str):
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
