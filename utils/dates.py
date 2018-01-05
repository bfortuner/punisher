import time
import datetime
import calendar


def utc_to_epoch(utc_time):
    return calendar.timegm(utc_time.utctimetuple())

def epoch_to_utc(epoch_sec):
    return datetime.datetime.utcfromtimestamp(epoch_sec)

def get_time_range(df, start_utc=None, end_utc=None):
    # df = dataframe
    if start_utc is not None:
        df = df[df.index >= utc_to_epoch(start_utc)]
    if end_utc is not None:
        df = df[df.index < utc_to_epoch(end_utc)]
    return df