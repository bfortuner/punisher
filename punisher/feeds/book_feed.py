import os
import datetime
import pandas as pd
from pathlib import Path

import punisher.config as cfg
import punisher.constants as c
from punisher.exchanges import ex_cfg
from punisher.portfolio.asset import Asset
from punisher.trading import coins
from punisher.utils.dates import get_time_range
from punisher.utils.dates import epoch_to_utc, utc_to_epoch
from punisher.utils.dates import str_to_date


ORDER_BOOK_KEYS = {}

class BookData():
    def __init__(self, book_df):
        self.book_df = book_df

    @property
    def df(self):
        return self.book_df

    def __len__(self):
        return len(self.book_df)


class BookFeed():
    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end
        self.prior_time = None
        self.book_df = None

    def initialize(self):
        if self.start is None:
            self.start = datetime.datetime(1, 1, 1, 1, 1)
        if self.end is None:
            self.end = datetime.datetime.utcnow()
        self.prior_time = self.start - datetime.timedelta(minutes=1)

    def update(self):
        pass

    def history(self, t_minus=0):
        pass

    def peek(self):
        pass

    def next(self, refresh=False):
        pass

    def __len__(self):
        return len(self.book_df)


# Helpers


def get_book_fname(exchange_id, asset):
    fname = '{:s}_{:s}.csv'.format(
        exchange_id, asset.id)
    return fname

def get_book_fpath(asset, exchange_id, outdir=cfg.DATA_DIR):
    fname = get_ohlcv_fname(asset, exchange_id)
    return Path(outdir, fname)

def fetch_book(exchange, asset, timeframe, start, end=None):
    print("Downloading:", asset.symbol)
    assert timeframe.id in exchange.timeframes
    end = datetime.datetime.utcnow() if end is None else end
    data = exchange.fetch_ohlcv(asset, timeframe, start)
    df = make_asset_df(data, asset, exchange.id, start, end)
    print("Downloaded rows:", len(df))
    return df

def fetch_and_save_book(exchange, asset, timeframe, start, end=None):
    df = fetch_asset(exchange, asset, timeframe, start, end)
    fpath = get_ohlcv_fpath(asset, exchange.id, timeframe)
    df.to_csv(fpath, index=True)
    return df

def update_local_book_cache(exchange, asset, timeframe, start, end=None):
    fpath = get_ohlcv_fpath(asset, exchange.id, timeframe)
    if os.path.exists(fpath):
        df = fetch_asset(exchange, asset, timeframe, start, end)
        df = merge_asset_dfs(df, fpath)
    else:
        df = fetch_and_save_asset(exchange, asset, timeframe, start, end)
    return df

def download_book(exchanges, assets, timeframe, start, end=None, update=False):
    for ex in exchanges:
        for asset in assets:
            if update:
                _ = update_local_asset_cache(ex, asset, timeframe, start, end)
            else:
                _ = fetch_and_save_asset(ex, asset, timeframe, start, end)

def load_book(ex_id, asset, start=None, end=None):
    fpath = get_book_fpath(asset, ex_id)
    return load_asset(fpath, start, end)

def load_book_df(fpath, start=None, end=None):
    df = pd.read_csv(
        fpath, index_col='epoch',
        parse_dates=['utc'],
        date_parser=str_to_date)
    df.sort_index(inplace=True)
    df = get_time_range(df, start, end)
    return df

def load_multiple_books(exchange_ids, assets, start, end=None):
    return None

def make_book_df(data, asset, ex_id, start=None, end=None):
    return None

def merge_book_dfs(new_data, fpath):
    return None
