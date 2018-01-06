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
    def load_markets(self, reload=False):
        pass

    @abc.abstractmethod
    def get_markets(self):
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
    def fetch_tickers(self):
        pass

    @abc.abstractmethod
    def fetch_balance(self):
        pass

    @abc.abstractmethod
    def create_order(self, symbol, type, side, amount):
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
    def fetch_order(self, order_id):
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

    @staticmethod
    def calculate_market_price(order_book):
        bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None
        spread = (ask - bid) if (bid and ask) else None
        print ('market price', { 'bid': bid, 'ask': ask, 'spread': spread })
        return bid, ask, spread

    @abc.abstractmethod
    def calculate_fee(self):
        pass


class CCXTExchange(Exchange):

    def __init__(self, client):
        super().__init__(name, config)
        self.client = EXCHANGE_CLIENTS(name)(config)
        # TODO: figure out if we need to fetch markets here
        self.client.fetch_markets()

    def load_markets(self, reload=False):
        """
        Returns an associative array of markets indexed by trading symbol.
        If you want more control over the execution of your logic,
        preloading markets by hand is recommended.
        """
        return self.client.load_markets(reload)

    def get_markets(self):
        return self.client.markets if (self.client.markets) else self.load_markets()

    def fetch_ohlcv(self, symbol, timeframe):
        """
        Returns OHLCV for the symbol based on the time_period
        ex. fetch_ohlcv(btcusd, 1d)
        To see all timeframes for an exchange use timeframes property
        when hasFetchTickers is True as well
        """
        assert client.hasFetchOHLCV
        return self.client.fetch_ohlcv(symbol, timeframe)

    def fetch_order_book(self, symbol):
        """
        L1 order book aggregation is useless so we use L2:
        """
        return self.fetch_l2_price_aggregated_order_book(symbol)

    def fetch_l2_price_aggregated_order_book(self, symbol):
        """
        Returns sample-data/order-book.json
        The bids array is sorted by price in descending order.
        The asks array is sorted by price in ascending order.
        """
        return self.client.fetch_l2_order_book(symbol)

    def fetch_trades(self, symbol):
        """Returns flat array. (Most recent trade first)"""
        return self.client.fetch_trades(symbol)

    def fetch_my_trades(self, symbol, since, limit, params={}):
        """Returns flat array. (Most recent trade first)"""
        return self.client.fetch_my_trades(symbol, since, limit, params)

    def fetch_ticker(self, symbol):
        assert client.hasFetchTickers
        return self.client.fetch_ticker(symbol)

    def fetch_tickers(self):
        """Fetch all tickers at once"""
        assert client.hasFetchTickers
        return self.client.fetch_tickers()

    def fetch_balance(self):
        """Returns json in the format of sample-data/account_balance"""
        return self.client.fetch_balance()

    def create_limit_buy_order(self, symbol, amount, price, params={}):
        self.client.create_limit_buy_order(symbol, amount, price, params)

    def create_limit_sell_order(self, symbol, amount, price, params={}):
        self.client.create_limit_sell_order(symbol, amount, price, params)

    def create_market_buy_order(self, symbol, amount, params={}):
        self.client.create_market_buy_order(symbol, amount, params)

    def create_market_sell_order(self, symbol, amount, params={}):
        self.client.create_market_sell_order(symbol, amount, params)

    def cancel_order(self, order_id, symbol, params={}):
        # TODO: figure out if we need to add a symbol
        # and if this returns a response
        # https://github.com/ccxt/ccxt/wiki/Manual#cancelling-orders
        return self.client.cancel_order(order_id)

    def fetch_order(self, order_id, params={}):
        return self.client.fetch_order(order_id, params)

    def fetch_orders(self, symbol, since, limit, params={}):
        return self.client.fetch_orders(symbol, since, limit, params)

    def fetch_open_orders(self, symbol, since, limit, params={}):
        return self.client.fetch_open_orders(symbol, since, limit, params)

    def fetch_closed_orders(self, symbol, since, limit, params={}):
        return self.client.fetch_closed_orders(symbol, since, limit, params)

    def deposit(self, symbol):
        return NotImplemented

    def withdraw(self, currency, amount, address, params={}):
        """Returns json response sample-data/withdraw-response.json"""
        return self.client.withdraw(currency, amount, wallet)

    def get_timeframes(self):
        assert client.hasFetchTickers
        return self.client.timeframes

    def calculate_fee(self):
        pass

    def order_on_margin(self, price):
        assert margin_is_available(self.client.id)

class PaperExchange(Exchange):
    def __init__(self, name, config):
        super().__init__(name, config)

    def fetch_ohlcv(self):
        pass
    def load_markets(self, reload=False):
        pass
    def get_markets(self):
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
    def fetch_tickers(self):
        pass
    def fetch_balance(self):
        pass
    def create_limit_buy_order(self, symbol, amount, price):
        pass
    def create_limit_sell_order(self, symbol, amount, price):
        pass
    def create_market_buy_order(self, symbol, amount):
        pass
    def create_market_sell_order(self, symbol, amount):
        pass
    def cancel_order(self, order_id):
        pass
    def fetch_order(self, order_id):
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
