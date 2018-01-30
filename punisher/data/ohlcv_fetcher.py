import datetime
import json
import os
import time

import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry
from tenacity import wait_exponential
from tenacity import stop_after_attempt

import punisher.constants as c
import punisher.config as cfg
from punisher.clients import s3_client
from punisher.exchanges import load_exchange
from punisher.data.store import FileStore
from punisher.feeds import OHLCVExchangeFeed
from punisher.feeds import ohlcv_feed
from punisher.portfolio.asset import Asset
from punisher.utils.dates import Timeframe
from punisher.utils.dates import str_to_date
from punisher import utils


parser = argparse.ArgumentParser(description='OHLCV Fetcher')
parser.add_argument('-ex', '--exchange', help='one exchange id', type=str)
parser.add_argument('-sym', '--symbol', help='one symbol', type=str)
parser.add_argument('-t', '--timeframe', help='length of period (1m, 30m, 1h, 1d)', default='30m', type=str)
parser.add_argument('--start', help='start time yyyy-mm-dd', default=None, type=str)
parser.add_argument('--end', help='end time yyyy-mm-dd', default=None, type=str)
parser.add_argument('--upload', help='upload to s3', action='store_true')
parser.add_argument('--refresh', help='sleep seconds for rate limit', default=5, type=int)

OHLCV = 'ohlcv'
OHLCV_DIR = Path(cfg.DATA_DIR, OHLCV)
OHLCV_DIR.mkdir(exist_ok=True)

def get_rotating_ohlcv_fname(ex_id, asset, timeframe, start):
    fname = '{:s}_{:s}_{:s}_{:d}_{:d}_{:d}.json'.format(
        ex_id, asset.id, timeframe.id, start.year,
        start.month, start.day
    )
    return fname

def get_rotating_ohlcv_fpath(ex_id, asset, timeframe, start):
    fname = get_rotating_ohlcv_fname(ex_id, asset, timeframe, start)
    return Path(OHLCV_DIR, fname)

def get_s3_path(ex_id, asset, timeframe, start):
    fname = get_rotating_ohlcv_fname(ex_id, asset, timeframe, start)
    return OHLCV + '/' + fname

def upload_to_s3(ex_id, asset, timeframe, start):
    fpath = get_rotating_ohlcv_fpath(ex_id, asset, timeframe, start)
    s3_path = get_s3_path(ex_id, asset, timeframe, start)
    print('Uploading to s3:', s3_path)
    s3_client.upload_file(str(fpath), s3_path)

# @retry(
#     wait=wait_exponential(multiplier=1, max=10),
#     stop=stop_after_attempt(5))
def download_and_save(ex_id, asset, timeframe, start, end):
    exchange = load_exchange(ex_id)
    df = ohlcv_feed.fetch_asset(exchange, asset, timeframe, start, end)
    fpath = get_rotating_ohlcv_fpath(ex_id, asset, timeframe, start)
    df.to_csv(fpath, index=True)
    return df

def backfill(exchange_id, asset, timeframe, start, end, upload, refresh):
    df = None
    while end - start > timeframe.delta:
        print("Start:", start, "End:", end)
        df = download_and_save(exchange_id, asset, timeframe, start, end)
        print("Rows", len(df))
        if upload:
            upload_to_s3(exchange_id, asset, timeframe, start)
        start = df[['utc']].max()[0] + timeframe.delta
        time.sleep(refresh)
    return df, start

def run(exchange_id, asset, timeframe, start, end, upload, refresh):
    while True:
        df, start = backfill(
            exchange_id, asset, timeframe,
            start, end, upload, refresh)
        end = datetime.datetime.utcnow()

if __name__ == "__main__":
    args = parser.parse_args()
    exchange_id = args.exchange
    asset = Asset.from_symbol(args.symbol)
    timeframe = Timeframe.from_id(args.timeframe)
    start = str_to_date(args.start)
    end = str_to_date(args.end) if args.end is not None else None
    upload = args.upload
    refresh = args.refresh
    print('Downloading OHLCV for: ', exchange_id,
           'Assets:', asset.symbol, 'timeframe:', timeframe.id,
           'start:', start, 'end:', end, 'refresh:', refresh)
    if end is None:
        print("Running forever!")
        end = datetime.datetime.utcnow()
        run(exchange_id, asset, timeframe, start, end, upload, refresh)
    else:
        print("Backfilling!")
        backfill(exchange_id, asset, timeframe, start, end, upload, refresh)
