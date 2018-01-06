import abc
import ccxt

import config as cfg
import constants as c


EXCHANGE_CLIENTS = {
    c.BINANCE: ccxt.binance,
    c.POLONIEX: ccxt.poloniex,
    c.GDAX: ccxt.gdax,
}

EXCHANGE_CONFIGS = {
    c.POLONIEX: {
        'apiKey': cfg.POLONIEX_API_KEY,
        'secret': cfg.POLONIEX_API_SECRET_KEY,
    },
    c.GDAX: {
        'apiKey': cfg.GDAX_API_KEY,
        'secret': cfg.GDAX_API_SECRET_KEY,
        'password': cfg.GDAX_PASSPHRASE,
        'verbose':False,
    },
    c.BINANCE: {},
    c.PAPER: {}
}


def load_exchange(name, config=None):
    """
    exchange_id: ['poloniex', 'simulate', 'gdax']
    c.EX
    """
    if name not in EXCHANGE_CONFIGS.keys():
        raise NotImplemented

    if config is None:
        config = EXCHANGE_CONFIGS[name]

    if name == c.PAPER:
        return PaperExchange(name, config)

    return CCXTExchange(name, config)


class Exchange(metaclass=abc.ABCMeta):

    def __init__(self, name, config):
        self.name = name
        self.config = config

    @abc.abstractmethod
    def fetch_ohlcv(self):
        pass

    @abc.abstractmethod
    def fetch_balance(self):
        pass

    @abc.abstractmethod
    def calculate_fee(self):
        pass

    @abc.abstractmethod
    def fetch_order(self, order):
        """:order Order object"""
        pass

    @abc.abstractmethod
    def create_limit_buy_order(self):
        pass

    @abc.abstractmethod
    def create_limit_sell_order(self):
        pass

    @abc.abstractmethod
    def cancel_order(self, order):
        pass


class CCXTExchange(Exchange):

    def __init__(self, name, config):
        super().__init__(name, config)
        self.client = EXCHANGE_CLIENTS(name)

    def fetch_ohlcv(self, symbol):
        self.client.fetch_ohlcv(symbol)

    def fetch_balance(self):
        self.client.fetch_balance(symbol)

    def calculate_fee(self):
        self.ex.calculate_fee()

    def fetch_order(self, order):
        self.ex.fetch_order()

    def create_limit_buy_order(self):
        self.ex.create_limit_buy_order()

    def create_limit_sell_order(self):
        self.ex.create_limit_sell_order()

    def cancel_order(self, order):
        self.ex.cancel_order()

    def order_on_margin(self, price):
        assert margin_is_available(self.ex.id)


class PaperExchange(Exchange):
    def __init__(self, name, config):
        super().__init__(name, config)

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
