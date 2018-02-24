import asyncio
from punisher.clients.gdax import gdax

import punisher.config as cfg

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

async def run_orderbook(product_ids):
    async with gdax.orderbook.OrderBook(
        product_ids=product_ids,
        api_key=cfg.GDAX_API_KEY,
        api_secret=cfg.GDAX_API_SECRET_KEY,
        passphrase=cfg.GDAX_PASSPHRASE,
    ) as orderbook:
        while True:
            message = await orderbook.handle_message()
            if message is None:
                continue
            print('ETH-USD ask: %s bid: %s' %
                  (orderbook.get_ask('ETH-USD'),
                   orderbook.get_bid('ETH-USD')))

if __name__ == '__main__':
    product_ids = ['ETH-USD']
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_orderbook(product_ids))
