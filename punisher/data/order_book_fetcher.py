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

from punisher.clients import s3_client
from punisher.exchanges import load_exchange
from punisher.data.store import FileStore
from punisher import utils
from punisher.portfolio.asset import Asset
import punisher.constants as c
import punisher.config as cfg

# also cool to check out
# https://github.com/google/python-fire

parser = argparse.ArgumentParser(description='Order Book Fetcher')
parser.add_argument('-ex', '--exchanges', help='exchange ids', nargs='+', type=str)
parser.add_argument('-sym', '--symbols', help='asset symbols', nargs='+', type=str)
parser.add_argument('-d', '--depth', help='# of bids/asks', default=None, type=int)
parser.add_argument('-r', '--refresh', help='fetch new data (seconds)', default=60, type=int)
parser.add_argument('--upload', help='upload to s3', action='store_true')

ORDER_BOOK = 'order_book'
ORDER_BOOK_DIR = Path(cfg.DATA_DIR, ORDER_BOOK)
ORDER_BOOK_DIR.mkdir(exist_ok=True)
S3_FOLDER = None

def get_order_book_fname(ex_id, asset):
    cur_time = datetime.datetime.utcnow()
    fname = '{:s}_{:s}_{:d}_{:d}_{:d}.json'.format(
        ex_id, asset.id, cur_time.year,
        cur_time.month, cur_time.day
    )
    return fname

def get_s3_path(ex_id, asset):
    fname = get_order_book_fname(ex_id, asset)
    return ORDER_BOOK + '/' + fname

# https://github.com/jd/tenacity
@retry(
    wait=wait_exponential(multiplier=1, max=10),
    stop=stop_after_attempt(5))
def download_and_save_order_book_data(exchange_id, asset, depth):
    exchange = load_exchange(exchange_id)
    depth = {} if depth is None else {'depth': depth}
    data = exchange.fetch_order_book(asset, depth)
    fname = get_order_book_fname(exchange_id, asset)
    fpath = Path(ORDER_BOOK_DIR, fname)
    utils.files.save_dct(fpath, data, mode='a+')
    return fpath

def run(exchange_ids, assets, depth, upload):
    for ex_id in exchanges:
        for asset in assets:
            print('Downloading', ex_id, asset.symbol)
            fpath = download_and_save_order_book_data(ex_id, asset, depth)
            if upload:
                s3_path = get_s3_path(ex_id, asset)
                print('Uploading to s3:' ,s3_path)
                s3_client.upload_file(str(fpath), s3_path)


if __name__ == "__main__":
    args = parser.parse_args()
    exchanges = args.exchanges
    assets = [Asset.from_symbol(s) for s in args.symbols]
    depth = args.depth
    refresh = args.refresh
    upload = args.upload
    print('Downloading order book for: ', args.exchanges,
           'Assets:', args.symbols, 'refresh sec:', refresh)

    while True:
        run(exchanges, assets, depth, upload)
        time.sleep(refresh)
