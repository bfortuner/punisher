import concurrent.futures
import json
import os
import time
from punisher.exchanges.exchange import load_exchange
from punisher.data.store import FileStore
from punisher.utils import files
from punisher.portfolio.asset import Asset
import punisher.constants as c

exchange_names = [c.BINANCE]
symbols = ['ETH/BTC', 'XRP/BTC', 'TRX/BTC']

data_name_base = 'order_book'
fname = 'multiasset'
store = FileStore(os.path.join("./order_book_data", data_name_base))
store.initialize()

exchanges = []

for ex in exchange_names:
    exchanges.append(load_exchange(ex))

assets = []
for symbol in symbols:
    assets.append(Asset.from_symbol(symbol))

# create the asset files
for ex in exchanges:
    for asset in assets:
        store.save_json(ex.id + "-" + asset.id, [])

def download_and_save_order_book_data(ex, assets=assets):
    for asset in assets:
        data = ex.fetch_order_book(asset)
        jsn = store.load_json(ex.id + "-" + asset.id)
        # If previous data is older than new data
        if not jsn:
            jsn.append(data)
            store.save_json(ex.id + "-" + asset.id, jsn)
        elif jsn[-1]['timestamp'] < data['timestamp']:
            jsn.append(data)
            store.save_json(ex.id + "-" + asset.id, jsn)

while True:
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        for res in executor.map(download_and_save_order_book_data, exchanges):
            print("fetching data...")
    time.sleep(1)
