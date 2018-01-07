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
    c.BINANCE: {
        'apiKey': cfg.BINANCE_API_KEY,
        'secret': cfg.BINANCE_API_SECRET_KEY,
    },
    c.PAPER: {}
}


def load_exchange(ex_id, config=None):
    """
    exchange_id: ['poloniex', 'simulate', 'gdax']
    c.EX
    """
    if ex_id not in EXCHANGE_CONFIGS.keys():
        raise NotImplemented

    if config is None:
        config = EXCHANGE_CONFIGS[ex_id]

    if ex_id == c.PAPER:
        return PaperExchange(ex_id, config)

    return CCXTExchange(ex_id, config)


class Exchange(metaclass=abc.ABCMeta):

    def __init__(self, id_, config):
        self.id = id_
        self.config = config

    @abc.abstractmethod
    def get_markets(self):
        pass

    @abc.abstractmethod
    def fetch_order_book(self, symbol):
        pass

    @abc.abstractmethod
    def fetch_public_trades(self, symbol):
        pass

    @abc.abstractmethod
    def fetch_ticker(self, symbol):
        pass

    @abc.abstractmethod
    def fetch_balance(self):
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
    def fetch_order_book(self, symbol):
        pass

    @abc.abstractmethod
    def fetch_ohlcv(self, symbol):
        pass

    @abc.abstractmethod
    def fetch_order(self, order_id, symbol=None, params=None):
        pass

    @abc.abstractmethod
    def fetch_orders(self, symbol, since=None, limit=None, params=None):
        pass

    @abc.abstractmethod
    def fetch_open_orders(self, symbol, since=None, limit=None, params=None):
        pass

    @abc.abstractmethod
    def fetch_closed_orders(self, symbol, since=None, limit=None, params=None):
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

    def get_default_params_if_none(self, params):
        return {} if params is None else params


class CCXTExchange(Exchange):

    def __init__(self, id_, config):
        super().__init__(id_, config)
        self.client = EXCHANGE_CLIENTS[id_](config)
        self.client.fetch_markets()

    def get_markets(self):
        if self.client.markets is None:
            return self.client.load_markets(reload=True)
        return self.client.markets

    def fetch_ohlcv(self, symbol, period):
        """
        Returns OHLCV for the symbol based on the time_period
        ex. fetch_ohlcv(btcusd, 1d)
        To see all timeframes for an exchange use timeframes property
        when hasFetchTickers is True as well
        """
        assert self.client.hasFetchOHLCV
        assert period in self.timeframes
        return self.client.fetch_ohlcv(symbol, period)

    def fetch_order_book(self, symbol):
        """
        https://github.com/ccxt/ccxt/wiki/Manual#order-book--market-depth
        Most common level of aggregation where order volumes are grouped
        by price. If two orders have the same price, they appear as one
        single order for a volume equal to their total sum.

        Returns sample-data/order-book.json
        The bids array is sorted by price in descending order.
        The asks array is sorted by price in ascending order.
        """
        return self.client.fetch_l2_order_book(symbol)

    def fetch_public_trades(self, symbol):
        """Returns list of most recent trades for a particular symbol"""
        return self.client.fetch_trades(symbol)

    def fetch_ticker(self, symbol):
        return self.client.fetch_ticker(symbol)

    def fetch_balance(self):
        """Returns json in the format of sample-data/account_balance"""
        return self.client.fetch_balance()

    def create_limit_buy_order(self, symbol, amount, price, params=None):
        params = self.get_default_params_if_none(params)
        return self.client.create_limit_buy_order(symbol, amount, price, params)

    def create_limit_sell_order(self, symbol, amount, price, params=None):
        params = self.get_default_params_if_none(params)
        return self.client.create_limit_sell_order(symbol, amount, price, params)

    def create_market_buy_order(self, symbol, amount, params=None):
        params = self.get_default_params_if_none(params)
        return self.client.create_market_buy_order(symbol, amount, params)

    def create_market_sell_order(self, symbol, amount, params=None):
        params = self.get_default_params_if_none(params)
        return self.client.create_market_sell_order(symbol, amount, params)

    def cancel_order(self, order_id, symbol=None, params=None):
        """https://github.com/ccxt/ccxt/wiki/Manual#cancelling-orders"""
        params = self.get_default_params_if_none(params)
        return self.client.cancel_order(order_id)

    def fetch_order(self, order_id, symbol, params=None):
        """https://github.com/ccxt/ccxt/wiki/Manual#orders"""
        params = self.get_default_params_if_none(params)
        return self.client.fetch_order(order_id, symbol, params)

    def fetch_orders(self, symbol, since=None, limit=None, params=None):
        params = self.get_default_params_if_none(params)
        return self.client.fetch_orders(symbol, since, limit, params)

    def fetch_open_orders(self, symbol, since=None, limit=None, params=None):
        params = self.get_default_params_if_none(params)
        return self.client.fetch_open_orders(symbol, since, limit, params)

    def fetch_closed_orders(self, symbol, since=None, limit=None, params=None):
        params = self.get_default_params_if_none(params)
        return self.client.fetch_closed_orders(symbol, since, limit, params)

    def deposit(self, symbol):
        return NotImplemented

    def withdraw(self, currency, amount, address, params=None):
        params = self.get_default_params_if_none(params)
        return NotImplemented

    @property
    def timeframes(self):
        return self.client.timeframes

    def calculate_fee(self, symbol, type, side, amount, price,
                      taker_or_maker='taker', params=None):
        params = self.get_default_params_if_none(params)
        return self.client.calculate_fee(
            symbol, type, side, amount, price,
            taker_or_maker, params)




class PaperExchange(Exchange):
    def __init__(self, id_, config, data_provider):
        super().__init__(id_, config)
        self.data_provider = data_provider
        self.orders = []
        self.balance = {}
        self.commissions = []

    def get_markets(self):
        return self.data_provider.get_markets()

    def fetch_ohlcv(self, symbol, timeframe):
        return self.data_provider.fetch_ohlcv(symbol, timeframe)

    def fetch_order_book(self, symbol):
        return self.data_provider.fetch_l2_order_book(symbol)

    def fetch_public_trades(self, symbol):
        """Returns list of most recent trades for a particular symbol"""
        return self.data_provider.fetch_trades(symbol)

    def fetch_my_trades(self, symbol, since, limit, params=None):
        """Returns list of most recent trades for a particular symbol"""
        return self.data_provider.fetch_my_trades(symbol, since, limit, params)

    def fetch_ticker(self, symbol):
        return self.data_provider.fetch_ticker(symbol)

    def fetch_tickers(self):
        """Fetch all tickers at once"""
        return self.data_provider.fetch_tickers()

    """Paper trading methods"""

    def fetch_balance(self):
        """Returns json in the format of sample-data/account_balance"""
        return self.data_provider.fetch_balance()

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
