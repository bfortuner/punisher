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


TRADE_COLUMNS = [
    'id', 'exchange_id', 'exchange_order_id', 'price',
    'quantity', 'trade_time', 'fee', 'side', 'symbol'
]
TRADES = 'trades'
TRADES_DIR = Path(cfg.DATA_DIR, TRADES)
TRADES_DIR.mkdir(exist_ok=True)


class TradeData():
    def __init__(self, trade_df):
        self.trade_df = trade_df

    @property
    def df(self):
        return self.trade_df

    def __len__(self):
        return len(self.trade_df)


class TradeFeed():
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
        return len(self.trade_df)



# Helpers

def get_rotating_trades_fname(ex_id, asset, start):
    fname = '{:s}_{:s}_{:d}_{:d}_{:d}_{:d}.csv'.format(
        ex_id, asset.id, start.year, start.month, start.day, start.hour
    )
    return fname

def get_rotating_trades_fpath(ex_id, asset, start, outdir=TRADES_DIR):
    fname = get_rotating_trades_fname(ex_id, asset, start)
    return Path(outdir, fname)

def fetch_trades(exchange, asset, start=None, end=None):
    print("Downloading trades:", asset.symbol)
    trades = exchange.fetch_public_trades(asset, start, end)
    data = [t.to_dict() for t in trades]
    df = make_trades_df(data)
    print("Downloaded rows:", len(df))
    return df

def fetch_and_save_trades(exchange, asset, start, end=None):
    df = fetch_trades(exchange, asset, start, end)
    fpath = get_rotating_trades_fpath(exchange.id, asset, start)
    df.to_csv(fpath, index=True)
    return df

def update_local_trades_cache(exchange, asset, start, end=None):
    fpath = get_rotating_trades_fpath(exchange.id, asset, start)
    if os.path.exists(fpath):
        df = fetch_trades(exchange, asset, start, end)
        df = merge_trades_dfs(df, fpath)
    else:
        df = fetch_and_save_trades(exchange, asset, start, end)
    return df

def load_trades(ex_id, asset, start):
    # Year,Month,Day,Hour
    fpath = get_rotating_trades_fpath(ex_id, asset, start)
    return load_trades_df(fpath)

def load_trades_df(fpath):
    df = pd.read_csv(
        fpath, index_col='id',
        parse_dates=['trade_time'],
        date_parser=str_to_date)
    df.sort_index(inplace=True)
    return df

def make_trades_df(data):
    df = pd.DataFrame(data, columns=TRADE_COLUMNS)
    df['trade_time'] = [str_to_date(d) for d in df['trade_time']]
    df.set_index('id', inplace=True)
    df.sort_values(by='trade_time', inplace=True)
    return df

def merge_trades_dfs(new_data, fpath):
    cur_df = pd.read_csv(
        fpath, index_col='id',
        parse_dates=['trade_time'],
        date_parser=str_to_date)
    new_df = pd.DataFrame(new_data)
    cur_df = pd.concat([cur_df, new_df])
    cur_df = cur_df[~cur_df.index.duplicated(keep='last')]
    cur_df.to_csv(fpath, index=True)
    cur_df.sort_values(by='trade_time', inplace=True)
    return cur_df

def load_multiple_trades(exchange_ids, assets, start, end=None):
    return None

def download_trades(exchanges, assets, start, update=False):
    for ex in exchanges:
        for asset in assets:
            if update:
                _ = update_local_trades_cache(ex, asset, start)
            else:
                _ = fetch_and_save_trades(ex, asset, start)
