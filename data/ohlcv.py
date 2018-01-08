import os
import datetime
import pandas as pd

import config as cfg
import constants as c

import utils.dates
from utils.dates import get_time_range
from utils.dates import epoch_to_utc, utc_to_epoch
from utils.dates import str_to_date
from trading.coins import get_symbol
from portfolio.asset import Asset


def get_price_data_fpath(asset, exchange_id, period):
    fname = '{:s}_{:s}_{:s}.csv'.format(
        exchange_id, asset.id, str(period))
    return os.path.join(cfg.DATA_DIR, fname)


def fetch_ohlcv_data(exchange, asset, period, start, end=None):
    print("Downloading:", asset.symbol)
    assert period in exchange.timeframes
    end = datetime.datetime.utcnow() if end is None else end
    data = exchange.fetch_ohlcv(asset, period)
    df = make_ohlcv_df(data, start, end)
    print("Downloaded rows:", len(df))
    return df


def fetch_and_save_ohlcv_data(exchange, asset, period, start, end=None):
    df = fetch_ohlcv_data(exchange, asset, period, start, end)
    fpath = get_price_data_fpath(asset, exchange.id, period)
    df.to_csv(fpath, index=True)
    return df


def update_local_ohlcv_data(exchange, asset, period, start, end=None):
    fpath = get_price_data_fpath(asset, exchange.id, period)
    if os.path.exists(fpath):
        df = fetch_ohlcv_data(exchange, asset, period, start, end)
        df = merge_local_csv_feeds(df, fpath)
    else:
        df = fetch_and_save_ohlcv_data(exchange, asset, period, start, end)
    return df


def load_chart_data_from_file(fpath, start=None, end=None):
    df = pd.read_csv(
        fpath, index_col='time_epoch',
        parse_dates=['time_utc'],
        date_parser=str_to_date)
    df.sort_index(inplace=True)
    df = get_time_range(df, start, end)
    return df


def download_chart_data(exchange, assets, period, start, end=None):
    for asset in assets:
        update_local_ohlcv_data(exchange, asset, period, start, end)


def load_multiple_assets(exchange_id, assets, period, start, end=None):
    df = pd.DataFrame()
    for asset in assets:
        fpath = get_price_data_fpath(asset, exchange_id, period)
        data = load_chart_data_from_file(fpath, start, end)
        df[asset.id] = data['close']
    df.dropna(inplace=True)
    df['time_utc'] = [epoch_to_utc(t) for t in df.index]
    return df


def make_ohlcv_df(data, start=None, end=None):
    df = pd.DataFrame(data, columns=c.OHLCV_COLUMNS)
    df['time_epoch'] = df['time_epoch'] // 1000 # ccxt includes millis
    df['time_utc'] = [epoch_to_utc(t) for t in df['time_epoch']]
    df.set_index('time_epoch', inplace=True)
    df.sort_index(inplace=True)
    df = get_time_range(df, start, end)
    return df


def merge_local_csv_feeds(new_data, fpath):
    cur_df = pd.read_csv(
        fpath, index_col='time_epoch',
        parse_dates=['time_utc'],
        date_parser=str_to_date)
    new_df = pd.DataFrame(new_data)
    cur_df = pd.concat([cur_df, new_df])
    cur_df = cur_df[~cur_df.index.duplicated(keep='last')]
    cur_df.to_csv(fpath, index=True)
    return cur_df
