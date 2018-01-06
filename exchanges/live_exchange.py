import ccxt
from helpers.cctx import init_exchange
from exchanges import Exchange

# hitbtc = ccxt.hitbtc({'verbose': True})
# bitmex = ccxt.bitmex()
# huobi  = ccxt.huobi()
# exmo   = ccxt.exmo({
#     'apiKey': 'YOUR_PUBLIC_API_KEY',
#     'secret': 'YOUR_SECRET_PRIVATE_KEY',
# })

# hitbtc_markets = hitbtc.load_markets()

# print(hitbtc.id, hitbtc_markets)
# print(bitmex.id, bitmex.load_markets())
# print(huobi.id, huobi.load_markets())

# print(hitbtc.fetch_order_book(hitbtc.symbols[0]))
# print(bitmex.fetch_ticker('BTC/USD'))
# print(huobi.fetch_trades('LTC/CNY'))

# print(exmo.fetch_balance())

# # sell one ฿ for market price and receive $ right now
# print(exmo.id, exmo.create_market_sell_order('BTC/USD', 1))

# # limit buy BTC/EUR, you pay €2500 and receive ฿1  when the order is closed
# print(exmo.id, exmo.create_limit_buy_order('BTC/EUR', 1, 2500.00))

# # pass/redefine custom exchange-specific order params: type, amount, price, flags, etc...
# kraken.create_market_buy_order('BTC/USD', 1, {'trading_agreement': 'agree'})

class LiveExchange(Exchange):

    def __init__(self, exchange_id, exchange_cfg):
        exchange = init_exchange(exchange_id, exchange_cfg)
        pass

    def fetch_ohlcv(self):
        pass

    def fetch_balance(self):
        pass

    def calculate_fee(self):
        pass

    def fetch_order(self, order):
        pass

    def create_limit_buy_order(self):
        pass

    def create_limit_sell_order(self):
        pass

    def cancel_order(self, order):
        pass