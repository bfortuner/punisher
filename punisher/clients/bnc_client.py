import datetime

import numpy as np
import pandas as pd
import requests

import punisher.config as cfg
from punisher.exchanges import ex_cfg
from punisher.feeds import ohlcv_feed
from punisher.utils.dates import utc_to_local
from punisher.utils.dates import epoch_to_utc


BNC_EXCHANGE_RATE_ENDPOINT = 'https://bravenewcoin-mwa-historic-v1.p.mashape.com/mwa-historic'
REQUEST_SIZE = 1000

def merge_dfs(df1, df2):
    df = pd.concat([df1, df2])
    df = df[~df.index.duplicated(keep='last')]
    return df

def get_bnc_data(asset, start, end):
    start = utc_to_local(start)
    end = utc_to_local(end)
    url = cfg.BNC_ENDPOINT + '/mwa-historic'
    params = {
        'coin': asset.base,
        'market': asset.quote,
        'from': round(start.timestamp()),
        'to': round(end.timestamp())
    }
    headers = {
        "X-Mashape-Key": cfg.BNC_API_KEY,
        "Accept": "application/json"
    }
    r = requests.get(url, headers=headers, params=params)
    data = r.json()['data']
    data = np.round(np.asarray(data).astype(float),5)
    # Duplicate close column for CCXT OHLCV consistency
    data = data[:,[0,3,3,3,3,4]]

    return data

def fetch_asset(asset, timeframe, start, end):
    print((end - start).total_seconds(), REQUEST_SIZE * timeframe.delta.seconds)
    cur_time = start
    timerange_delta = datetime.timedelta(
        seconds=min((end - start).total_seconds(),
        REQUEST_SIZE * timeframe.delta.seconds)
    )
    df = None
    while cur_time < end:
        data = get_bnc_data(asset, cur_time, cur_time + timerange_delta)
        last_epoch = np.max(data[:,0])
        print("last_epoch", last_epoch)
        last_time = epoch_to_utc(np.max(data[:,0]))
        print("lasttime", last_time)
        if cur_time > last_time:
            break
        cur_time = last_time + timeframe.delta
        # Convert to millis to match CCXT timestamp
        data[:,0] *= 1000
        new_df = ohlcv_feed.make_asset_df(data, asset, ex_cfg.BNC)
        if df is not None:
            df = merge_dfs(df, new_df)
        else:
            df = new_df
    return df
