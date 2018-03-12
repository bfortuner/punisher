import os
import asyncio
from pathlib import Path

import punisher.config as cfg
from punisher.clients.gdax import gdax
from punisher.clients import s3_client
from punisher.utils.dates import utc_to_epoch
import punisher.utils.files as file_utils


"""
Message Types:

Done {
'type': 'done', 'side': 'buy',
'order_id': '74f8d850-31fc-4de4-9d21-157ddd6bd6f2',
'reason': 'canceled', 'product_id': 'ETH-USD',
'price': '842.24000000', 'remaining_size': '9.00000000',
'sequence': 2680535089, 'time': '2018-02-23T05:35:39.322000Z'}

Open {'type': 'open', 'side': 'sell', 'price': '845.90000000',
'order_id': 'a88b31f6-4460-4447-8c1d-e0ae952ff8cb',
'remaining_size': '9.00000000', 'product_id': 'ETH-USD',
'sequence': 2680535091, 'time': '2018-02-23T05:35:39.327000Z'}


Match {
'type': 'match', 'trade_id': 29624440,
'maker_order_id': '6ce291c2-8409-4cfc-b7f3-d7482add82cf',
'taker_order_id': '95a402e1-ca40-4ed2-919b-24e239081733',
'side': 'sell', 'size': '2.37620000', 'price': '844.00000000',
'product_id': 'ETH-USD', 'sequence': 2680554179,
'time': '2018-02-23T05:37:14.576000Z'}
"""

TIMEOUT_SEC = 10
ORDER_BOOK = 'order_book'
ORDER_BOOK_DIR = Path(cfg.DATA_DIR, ORDER_BOOK)
ORDER_BOOK_DIR.mkdir(exist_ok=True)
MAX_RETRIES = 15
LEVEL = 3

def get_order_book_fname(ex_id, asset, level, epoch_time):
    fname = '{:s}_{:s}_{:d}_{:d}.json'.format(
        ex_id, asset.id, level, epoch_time)
    return fname

def get_s3_path(ex_id, asset, level, epoch_time):
    fname = get_order_book_fname(ex_id, asset, level, epoch_time)
    return ORDER_BOOK + '/' + fname

async def save_orderbook(asset, book, timestamp, upload, cleanup):
    fname = get_order_book_fname(ex_cfg.GDAX, asset, LEVEL, timestamp)
    fpath = Path(ORDER_BOOK_DIR, fname)
    file_utils.save_dct(fpath, data, mode='w')
    if upload:
        s3_path = get_s3_path(ex_cfg.GDAX, asset, LEVEL, timestamp)
        s3_client.upload_file(str(fpath), s3_path)
        if cleanup:
            os.remove(fpath)

async def handle_missed_msg(msg, orderbook, upload, cleanup):
    print("Missed Msg:", msg['product_id'], msg['sequence'])
    await asyncio.sleep(0)
    utc_time = datetime.datetime.utcnow()
    timestamp = utc_to_epoch(utc_time) * 1000
    product_id = msg['product_id']
    asset = Asset.from_symbol(product_id)
    book = {
        'symbol': asset.symbol,
        'bids': orderbook._bids[product_id],
        'asks': orderbook._asks[product_id],
        'sequences': orderbook._sequences[product_id],
        'timestamp': timestamp,
        'datetime': utc_time
    }
    await save_orderbook(asset, book, timestamp, upload, cleanup)

async def handle_valid_msg(msg, orderbook, store):
    ## WRITE TO TIMESCALE DB ##
    print("Valid Trade:", msg)
    await asyncio.sleep(0)

# http://rickyhan.com/jekyll/update/2018/01/27/python36.html
async def run_orderbook(product_ids, upload, cleanup):
    loop = asyncio.get_event_loop()
    store = 5
    async with gdax.orderbook.OrderBook(
        product_ids=product_ids,
        api_key=cfg.GDAX_API_KEY,
        api_secret=cfg.GDAX_API_SECRET_KEY,
        passphrase=cfg.GDAX_PASSPHRASE,
    ) as orderbook:
        while True:
            msg = await orderbook.handle_message()
            print(msg)
            # if msg['status'] == 'VALID_MSG':
            #     await handle_valid_msg(msg, orderbook, store)
            # elif msg['status'] == 'MISSED_MSG':
            #     loop.create_task(handle_missed_msg(
            #         msg, orderbook, upload, cleanup))
            # else:
            #     print("Msg Status", msg['status'])


if __name__ == '__main__':
    product_ids = ['BTC-USD', 'ETH-USD', 'LTC-USD']
    upload = True
    cleanup = False
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_orderbook(product_ids, upload, cleanup))
