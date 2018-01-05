import os
import datetime
import pandas as pd

import config as cfg
import constants as c

import utils.dates
from utils.coins import get_symbol


def get_price_data_fpath(coin, market, exchange_id, period):
    fname = '{:s}_{:s}_{:s}_{:s}.csv'.format(
        exchange_id, coin, market, str(period))
    return os.path.join(cfg.DATA_DIR, fname)


def fetch_ohlcv_data(exchange, coin, market, period, start, end=None):
    """ 
    Start/End = time in UTC 
    """
    print("Downloading:", get_symbol(coin, market))
    assert period in exchange.timeframes
    end = datetime.datetime.utcnow() if end is None else end
    data = exchange.fetch_ohlcv(get_symbol(coin, market), period)
    df = make_ohlcv_df(data, start, end)
    print("Downloaded rows:", len(df))
    return df


def fetch_and_save_ohlcv_data(exchange, coin, market, period, start, end=None):
    df = fetch_ohlcv_data(exchange, coin, market, period, start, end)
    fpath = get_price_data_fpath(coin, market, exchange.id, period)
    df.to_csv(fpath, index=True)
    return df


def update_local_ohlcv_data(exchange, coin, market, period, start, end=None):
    fpath = get_price_data_fpath(coin, market, exchange.id, period)
    if os.path.exists(fpath):
        df = fetch_ohlcv_data(exchange, coin, market, period, start, end)
        df = merge_local_csv_feeds(df, fpath)
    else:
        df = fetch_and_save_ohlcv_data(exchange, coin, market, period, start, end)
    return df


def load_chart_data_from_file(fpath, start, end):
    df = pd.read_csv(fpath, index_col='time_epoch')
    df['time_utc'] = [utils.dates.epoch_to_utc(t) for t in df.index]
    df.sort_index(inplace=True)
    df = utils.dates.get_time_range(df, start, end)
    return df


def download_chart_data(exchange, coins, market, period, start, end=None):
    for coin in coins:
        update_local_ohlcv_data(exchange, coin, market, period, start, end)


def load_multi_coin_data(exchange_id, coins, market, period, start, end=None):
    df = pd.DataFrame()
    for coin in coins:
        symbol = get_symbol(coin, market)
        fpath = get_price_data_fpath(coin, market, exchange_id, period)
        data = load_chart_data_from_file(fpath, start, end)
        df[symbol] = data['close']
    df.dropna(inplace=True)
    df['time_utc'] = [utils.dates.epoch_to_utc(t) for t in df.index]
    return df


def make_ohlcv_df(data, start=None, end=None):
    df = pd.DataFrame(data, columns=c.OHLCV_COLUMNS)
    df['time_epoch'] = df['time_epoch'] // 1000 # ccxt includes millis
    df['time_utc'] = [utils.dates.epoch_to_utc(t) for t in df['time_epoch']] 
    df.set_index('time_epoch', inplace=True)
    df.sort_index(inplace=True)
    df = utils.dates.get_time_range(df, start, end)
    return df


def merge_local_csv_feeds(new_data, fpath):
    cur_df = pd.read_csv(fpath, index_col='time_epoch')
    cur_df['time_utc'] = [utils.dates.epoch_to_utc(t) for t in cur_df.index]
    new_df = pd.DataFrame(new_data)
    cur_df = pd.concat([cur_df, new_df])
    cur_df = cur_df[~cur_df.index.duplicated(keep='last')]
    cur_df.to_csv(fpath, index=True)
    return cur_df