import sys
import datetime
import json
import os
import re
import time
import traceback

import argparse
from pathlib import Path

import backoff
import pandas as pd

import punisher.constants as c
import punisher.config as cfg
from punisher.clients import s3_client
from punisher.exchanges import ex_cfg
from punisher.exchanges import load_exchange
from punisher.feeds import trade_feed
from punisher.portfolio.asset import Asset
from punisher.utils.dates import str_to_date
from punisher.utils.dates import utc_to_epoch
from punisher.utils.encoders import EnumEncoder
import punisher.utils.logger as logger_utils

from . import timescale_store as sql_store

parser = argparse.ArgumentParser(description='Trade Fetcher')
parser.add_argument('-ex', '--exchange', help='one exchange id', type=str)
parser.add_argument('-sym', '--symbol', help='one symbol', type=str)
parser.add_argument('--start', help='start time yyyy-mm-dd', default=None, type=str)
parser.add_argument('--end', help='end time yyyy-mm-dd', default=None, type=str)
parser.add_argument('--action', help='"fetch" from exchange, "download" from s3, or "list" files in S3',
                    choices=['fetch','download', 'list'])
parser.add_argument('--upload', help='upload to s3 after fetching from exchange', action='store_true')
parser.add_argument('--refresh', help='sleep seconds for rate limit', default=5, type=int)
parser.add_argument('--outdir', help='output directory to save files', default=cfg.DATA_DIR, type=str)
parser.add_argument('--cleanup', help='remove local copy of files after s3 upload', action='store_true')
parser.add_argument('--store', help='save to sql or file', choices=['sql','file'], default='file', type=str)

# python -m punisher.data.trade_fetcher -ex binance -sym ETH/BTC --start 2018-01-01 --action fetch --cleanup --upload --store file

args = parser.parse_args()
TRADES = 'trades'
TRADES_DIR = Path(args.outdir, TRADES)
TRADES_DIR.mkdir(exist_ok=True)
MAX_RETRIES = 15


def get_s3_path(ex_id, asset, start):
    fname = trade_feed.get_rotating_trades_fname(ex_id, asset, start)
    return TRADES + '/' + ex_id + '/' + asset.id + '/' + fname

def upload_to_s3(ex_id, asset, start):
    fpath = trade_feed.get_rotating_trades_fpath(ex_id, asset, start)
    s3_path = get_s3_path(ex_id, asset, start)
    print('Uploading to s3:', s3_path)
    s3_client.upload_file(str(fpath), s3_path)

@backoff.on_exception(backoff.expo,
                      Exception, #TODO: include ccxt exceptions only
                      on_backoff=logger_utils.retry_hdlr,
                      on_giveup=logger_utils.giveup_hdlr,
                      max_tries=MAX_RETRIES)
def fetch_once(ex_id, asset, start, end, upload, refresh, cleanup):
    print("Fetching for period Start:", start, "End:", end)
    exchange = load_exchange(ex_id)
    last_fpath = trade_feed.get_rotating_trades_fpath(ex_id, asset, start)
    while start < end:
        cur_end = start + datetime.timedelta(hours=24)
        print("Start:", start, "End:", cur_end)
        df = trade_feed.fetch_trades(exchange, asset, start, cur_end)

        if len(df) == 0:
            start += datetime.timedelta(minutes=5)
        else:
            fpath = trade_feed.get_rotating_trades_fpath(ex_id, asset, start)
            if os.path.exists(fpath):
                df = trade_feed.merge_trades_dfs(df, fpath)
            else:
                df.to_csv(fpath, index=True)

            if upload:
                upload_to_s3(ex_id, asset, start)

            if cleanup and fpath != last_fpath:
                os.remove(last_fpath)
                last_fpath = fpath
            start = df[['trade_time']].max()[0]

        time.sleep(refresh)
    return df, start

def fetch_forever(exchange_id, asset, start, end, upload, refresh, cleanup):
    while True:
        df, start = fetch_once(
            exchange_id, asset, start,
            end, upload, refresh, cleanup)
        end = datetime.datetime.utcnow()
        time.sleep(refresh)

def write_df_to_sql(df, table):
    trades = []
    for idx,row in df.iterrows():
        trades.append({
            'seq':idx,
            'ts': utc_to_epoch(row['trade_time'])*1000,
            'is_trade': True,
            'is_bid': row['side']=='BUY',
            'price': row['price'],
            'quantity': row['quantity']
        })
    sql_store.insert_or_update_trades(table, trades)

@backoff.on_exception(backoff.expo,
                      Exception, #TODO: include ccxt exceptions only
                      on_backoff=logger_utils.retry_hdlr,
                      on_giveup=logger_utils.giveup_hdlr,
                      max_tries=MAX_RETRIES)
def fetch_once_sql(ex_id, asset, start, end, refresh):
    print("Fetching / storing SQL for period Start:", start, "End:", end)
    exchange = load_exchange(ex_id)
    table = sql_store.get_trades_table(ex_id, asset)
    while start < end:
        cur_end = start + datetime.timedelta(hours=24)
        print("Start:", start, "End:", cur_end)
        df = trade_feed.fetch_trades(exchange, asset, start, cur_end)
        if len(df) == 0:
            delta = datetime.timedelta(minutes=5)
            if datetime.datetime.utcnow() > start + delta:
                start += datetime.timedelta(minutes=5)
            else:
                start += datetime.timedelta(seconds=1)
        else:
            write_df_to_sql(df, table)
            start = df[['trade_time']].max()[0]

        time.sleep(refresh)
    return start

def fetch_forever_sql(ex_id, asset, start, end, refresh):
    while True:
        start = fetch_once_sql(
            exchange_id, asset, start,
            end, refresh)
        end = datetime.datetime.utcnow()
        time.sleep(refresh)

def get_meta_from_fname(fname):
    reg = re.compile('([a-z]+)_([A-Z]+_[A-Z]+)_(20[0-9]+)_([0-9]+)_([0-9]+)_([0-9]+).csv')
    m = re.match(reg, fname)
    ex_id, asset_id, year, month, day, hour = m.groups()
    asset = Asset.from_symbol(asset_id)
    start = datetime.datetime(
        year=int(year), month=int(month), day=int(day), hour=int(hour))
    return ex_id, asset, start

def download(ex_id, asset, start, end=None):
    end = datetime.datetime.now() if end is None else end
    prefix = 'trades/' + ex_id + '/' + asset.id
    keys = s3_client.list_files(prefix=prefix)
    fpaths = []
    for key in keys:
        ex_id, asset, date = get_meta_from_fname(key.split('/')[-1])
        if date >= start and date < end:
            fpath = Path(TRADES_DIR, Path(key).name)
            fpaths.append(fpath)
            print("Downloading", fpath)
            s3_client.download_file(str(fpath), key)

def list_files():
    keys = s3_client.list_files(pattern=TRADES)
    reg = re.compile('trades\/[a-z]+\/[A-Z]+_[A-Z]+\/([a-z]+)_([A-Z]+_[A-Z]+)_(20[0-9]+)_([0-9]+)_([0-9]+)_([0-9]+).csv')
    meta = {}
    for key in keys:
        m = re.match(reg, key)
        if m is not None:
            ex_id, symbol, year, month, day, hour = m.groups()
            start = datetime.datetime(year=int(year), month=int(month),
                                      day=int(day), hour=int(hour))
            if ex_id not in meta:
                meta[ex_id] = {}
            if symbol not in meta[ex_id]:
                meta[ex_id][symbol] = {
                    'start': start,
                    'end': start
                }
            else:
                meta[ex_id][symbol] = {
                    'start': min(start, meta[ex_id][symbol]['start']),
                    'end': max(start, meta[ex_id][symbol]['end'])
                }
    return meta


if __name__ == "__main__":
    action = args.action
    exchange_id = args.exchange
    default_start = datetime.datetime.now() - datetime.timedelta(minutes=1)
    asset = Asset.from_symbol(args.symbol) if args.symbol is not None else None
    start = str_to_date(args.start) if args.start is not None else default_start
    end = str_to_date(args.end) if args.end is not None else None
    upload = args.upload
    cleanup = args.cleanup
    refresh = args.refresh

    if action == 'list':
        print('Listing Trade files in S3 for start time: {}, '
              'exchange: {}, asset: {}'.format(
              start, args.exchange, args.symbol))
        file_metadata = list_files()
        print(json.dumps(file_metadata, indent=4, cls=EnumEncoder))
    elif action == 'fetch':
        print('Fetching Trades from exchange: ', exchange_id,
               'Asset:', asset.symbol, 'start:', start, 'end:', end,
               'refresh:', refresh)
        if end is None:
            print("Running forever!")
            end = datetime.datetime.utcnow()
            if args.store == 'file':
                fetch_forever(exchange_id, asset, start, end, upload, refresh, cleanup)
            else:
                fetch_forever_sql(exchange_id, asset, start, end, refresh)
        else:
            print("Backfilling!")
            if args.store == 'file':
                fetch_once(exchange_id, asset, start, end, upload, refresh, cleanup)
            else:
                fetch_once_sql(exchange_id, asset, start, end, refresh)
    elif action == 'download':
        print('Downloading Trades from S3. ExchangeId:', exchange_id,
               'Asset:', asset.symbol, 'start:', start, 'end:', end)
        download(exchange_id, asset, start, end)

    else:
        raise Exception("Action {:s} not supported!".format(action))
