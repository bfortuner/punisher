import asyncio
import datetime
import json
import os
import time
import traceback
import itertools

import argparse
import backoff
from pathlib import Path

from punisher.portfolio.asset import Asset
from punisher.clients import s3_client
import punisher.constants as c
import punisher.config as cfg
from punisher.exchanges import load_exchange
import punisher.utils.files as file_utils
import punisher.utils.logger as logger_utils


parser = argparse.ArgumentParser(description='Order Book Fetcher')
parser.add_argument('-ex', '--exchanges', help='exchange ids', nargs='+', type=str)
parser.add_argument('-sym', '--symbols', help='asset symbols', nargs='+', type=str)
parser.add_argument('-l', '--level', help='Order book level (2,3)', default=2,
                    type=int, choices=[2,3])
parser.add_argument('-r', '--refresh', help='fetch new data (seconds)',
                    default=0, type=int)
parser.add_argument('--upload', help='upload to s3', action='store_true')
parser.add_argument('--cleanup', help='remove local files after upload',
                    action='store_true')

ORDER_BOOK = 'order_book'
ORDER_BOOK_DIR = Path(cfg.DATA_DIR, ORDER_BOOK)
ORDER_BOOK_DIR.mkdir(exist_ok=True)
L3_DEPTH = 1000
MAX_RETRIES = 15

def get_order_book_fname(ex_id, asset, level, epoch_time):
    fname = '{:s}_{:s}_{:d}_{:d}.json'.format(
        ex_id, asset.id, level, epoch_time)
    return fname

def get_s3_path(ex_id, asset, level, epoch_time):
    fname = get_order_book_fname(ex_id, asset, level, epoch_time)
    return ORDER_BOOK + '/' + fname

# https://github.com/ccxt/ccxt/wiki/Manual#error-handling
@backoff.on_exception(backoff.expo,
                      Exception, #TODO: include ccxt exceptions only
                      on_backoff=logger_utils.retry_hdlr,
                      on_giveup=logger_utils.giveup_hdlr,
                      max_tries=MAX_RETRIES)
async def fetch_order_book(exchange_id, asset, level, upload, cleanup):
    print('Fetching order book for:', exchange_id,
           'Asset:', asset.symbol, 'level:', level,
           'Time:', datetime.datetime.utcnow().isoformat())
    await asyncio.sleep(0)
    exchange = load_exchange(exchange_id)
    if level == 2:
        data = exchange.fetch_order_book(asset)
    else:
        data = exchange.fetch_raw_order_book(
            asset, depth=L3_DEPTH, level=3)

    fname = get_order_book_fname(exchange_id, asset, level, data['timestamp'])
    fpath = Path(ORDER_BOOK_DIR, fname)
    file_utils.save_dct(fpath, data, mode='a+')

    if upload:
        s3_path = get_s3_path(exchange_id, asset, level, data['timestamp'])
        s3_client.upload_file(str(fpath), s3_path)

        if cleanup:
            os.remove(fpath)

    return fpath

async def fetch_async(exchange_ids, assets, level, upload, cleanup):
    tasks = []
    for ex_id in exchange_ids:
        for asset in assets:
            tasks.append(fetch_order_book(ex_id, asset, level, upload, cleanup))
    done, pending = await asyncio.wait(tasks)

    for task in done:
        print(task.result())


if __name__ == "__main__":
    args = parser.parse_args()
    assets = [Asset.from_symbol(s) for s in args.symbols]

    if args.cleanup:
        assert args.upload is True

    print('Fetching order book for: ', args.exchanges,
           'Assets:', args.symbols, 'level:', args.level,
           'upload:', args.upload, 'cleanup:', args.cleanup,
           'refresh:', args.refresh)

    loop = asyncio.get_event_loop()
    try:
        if args.refresh > 0:
            while True:
                loop.run_until_complete(fetch_async(
                    args.exchanges, assets, args.level,
                    args.upload, args.cleanup))
                time.sleep(args.refresh)
        else:
            loop.run_until_complete(fetch_async(
                args.exchanges, assets, args.level,
                args.upload, args.cleanup))
    finally:
        loop.close()
