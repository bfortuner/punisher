import abc
import ccxt
import constants as c
import config as cfg

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
    def fetch_markets(self):
        pass

    @abc.abstractmethod
    def load_markets(self, reload=False):
        pass

    @abc.abstractmethod
    def fetch_order_book(self, symbol):
        pass

    @abc.abstractmethod
    def fetch_l2_price_aggregated_order_book(self, symbol):
        pass

    @abc.abstractmethod
    def fetch_trades(self, symbol):
        pass

    @abc.abstractmethod
    def fetch_my_trades(self, symbol):
        pass

    @abc.abstractmethod
    def fetch_ticker(self, symbol):
        pass

    @abc.abstractmethod
    def fetch_tickers(self, symbol):
        pass

    @abc.abstractmethod
    def fetch_balance(self):
        pass

    @abc.abstractmethod
    def createOrder(self, symbol, type, side, amount):
        pass

    @abc.abstractmethod
    def create_limit_buy_order(self, symbol, amount, price):
        pass

    @abc.abstractmethod
    def create_limit_sell_order(self, symbol, amount, price):
        pass

    @abc.abstractmethod
    def create_market_buy_order(self, symbol, amount):
        pass

    @abc.abstractmethod
    def create_market_sell_order(self, symbol, amount):
        pass

    @abc.abstractmethod
    def cancel_order(self, order_id):
        pass

    @abc.abstractmethod
    def fetch_order(self, order_id, symbol):
        pass

    @abc.abstractmethod
    def fetch_orders(self, symbol):
        pass

    @abc.abstractmethod
    def fetch_order_book(self, symbol):
        pass

    @abc.abstractmethod
    def fetch_ohlcv(self, symbol):
        pass

    @abc.abstractmethod
    def fetch_open_orders(self, symbol):
        pass

    @abc.abstractmethod
    def fetch_closed_orders(self, symbol):
        pass

    @abc.abstractmethod
    def deposit(self, symbol):
        pass

    @abc.abstractmethod
    def withdraw(self, symbol):
        pass

    @abc.abstractmethod
    def calculate_fee(self):
        pass


class CCXTExchange(Exchange):

    def __init__(self, client):
        super().__init__(name, config)
        self.client = EXCHANGE_CLIENTS(name)(config)

    def fetch_markets(self):
        self.client.fetch_markets()

    def load_markets(self, reload=False):
        """
        Returns an associative array of markets indexed by trading symbol.
        If you want more control over the execution of your logic,
        preloading markets by hand is recommended.
        """
        self.client.load_markets(reload)

    def fetch_order_book(self, symbol):
        self.client.fetch_order_book(symbol)

    def fetch_ohlcv(self, symbol):
        self.client.fetch_ohlcv(symbol)

    def fetch_l2_price_aggregated_order_book(self, symbol):
        self.client.fetch_l2_order_book(symbol)

    def fetch_trades(self, symbol):
        self.client.fetch_trades(symbol)

    def fetch_my_trades(self, symbol):
        self.client.fetch_my_trades(symbol)

    def fetch_ticker(self, symbol):
        self.client.fetch_ticker(symbol)

    def fetch_tickers(self, symbol):
        self.client.fetch_tickers(symbol)

    def fetch_balance(self):
        self.client.fetch_balance(symbol)

    def create_order(self, symbol, type, side, amount):
        self.client.create_order(symbol, type, side, amount)

    def create_limit_sell_order(self, symbol, amount, price):
        self.client.create_limit_sell_order(symbol, type, side, amount)

    def create_market_buy_order(self, symbol, amount):
        self.client.create_market_buy_order(symbol, amount)

    def create_market_sell_order(self, symbol, amount):
        self.client.create_market_sell_order(symbol, amount)

    def cancel_order(self, order_id):
        self.client.cancel_order(order_id)

    def fetch_order(self, order_id, symbol):
        self.client.fetch_order(order_id, symbol)

    def fetch_orders(self, symbol):
        self.client.fetch_orders(symbol)

    def fetch_open_orders(self, symbol):
        self.client.fetch_open_orders(symbol)

    def fetch_closed_orders(self, symbol):
        self.client.fetch_closed_orders(symbol)

    def deposit(self, symbol):
        self.client.fetch_closed_orders(symbol)

    def withdraw(self, symbol, amount, wallet):
        self.client.withdraw(symbol, amount, wallet)

    def calculate_fee(self):
        pass

    def order_on_margin(self, price):
        assert margin_is_available(self.client.id)


class PaperExchange(Exchange):
    def __init__(self, name, config):
        super().__init__(name, config)

    def fetch_ohlcv(self):
        pass
    def fetch_markets(self):
        pass
    def load_markets(self, reload=False):
        pass
    def fetch_order_book(self, symbol):
        pass
    def fetch_l2_price_aggregated_order_book(self, symbol):
        pass
    def fetch_trades(self, symbol):
        pass
    def fetch_my_trades(self, symbol):
        pass
    def fetch_ticker(self, symbol):
        pass
    def fetch_tickers(self, symbol):
        pass
    def fetch_balance(self):
        pass
    def create_order(self, symbol, type, side, amount):
        pass
    def create_limit_sell_order(self, symbol, amount, price):
        pass
    def create_market_buy_order(self, symbol, amount):
        pass
    def create_market_sell_order(self, symbol, amount):
        pass
    def cancel_order(self, order_id):
        pass
    def fetch_order(self, order_id, symbol):
        pass
    def fetch_orders(self, symbol):
        pass
    def fetch_open_orders(self, symbol):
        pass
    def fetch_closed_orders(self, symbol):
        pass
    def deposit(self, symbol):
        pass
    def withdraw(self, symbol, amount, wallet):
        pass
    def calculate_fee(self):
        pass
    def order_on_margin(self, price):
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
