import abc
import ccxt
import constants as c
import config as cfg
import uuid

from portfolio.asset import Asset
from portfolio.balance import Balance, BalanceType
from trading.order import Order, OrderType, OrderStatus
from trading.order import BUY_ORDER_TYPES, SELL_ORDER_TYPES
from data.data_provider import DataProvider, PaperExchangeDataProvider


EXCHANGE_CLIENTS = {
    c.BINANCE: ccxt.binance,
    c.POLONIEX: ccxt.poloniex,
    c.GDAX: ccxt.gdax,
}


class Exchange(metaclass=abc.ABCMeta):

    def __init__(self, id_, config):
        self.id = id_
        self.config = config

    @abc.abstractmethod
    def create_limit_buy_order(self, asset, quantity, price):
        pass

    @abc.abstractmethod
    def create_limit_sell_order(self, asset, quantity, price):
        pass

    @abc.abstractmethod
    def create_market_buy_order(self, asset, quantity):
        pass

    @abc.abstractmethod
    def create_market_sell_order(self, asset, quantity):
        pass

    @abc.abstractmethod
    def cancel_order(self, order_id):
        pass

    @abc.abstractmethod
    def deposit(self, asset):
        pass

    @abc.abstractmethod
    def withdraw(self, symbol, quantity, address, params=None):
        pass

    @staticmethod
    def calculate_market_price(order_book):
        bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None
        spread = (ask - bid) if (bid and ask) else None
        return { 'bid': bid, 'ask': ask, 'spread': spread }

    @abc.abstractmethod
    def calculate_fee(self):
        pass

    # Wrapper around balance method to give people the ability to
    # just ask if_balance_sufficient from the exchange without separately
    # requesting the balance
    def is_balance_sufficient(self, asset, quantity, price, order_type):
        return self.fetch_balance().is_balance_sufficient(
            asset, quantity, price, order_type)


    def get_default_params_if_none(self, params):
        return {} if params is None else params


class CCXTExchange(Exchange, DataProvider):

    def __init__(self, id_, config):
        # Removing super here in favor of init because
        # http://bit.ly/2qJ9RAP
        Exchange.__init__(self, id_, config)
        DataProvider.__init__(self, id_, config)
        self.client = EXCHANGE_CLIENTS[id_](config)
        self.client.fetch_markets()

    def get_markets(self):
        if self.client.markets is None:
            return self.client.load_markets(reload=True)
        return self.client.markets

    def fetch_ohlcv(self, asset, timeframe):
        """
        Returns OHLCV for the symbol based on the time_period
        ex. fetch_ohlcv(btcusd, 1d)
        To see all timeframes for an exchange use timeframes property
        when hasFetchTickers is True as well
        """
        assert self.client.hasFetchOHLCV
        return self.client.fetch_ohlcv(asset.symbol, timeframe)

    def fetch_order_book(self, asset):
        """
        https://github.com/ccxt/ccxt/wiki/Manual#order-book--mnrket-depth
        Most common level of aggregation where order volumes are grouped
        by price. If two orders have the same price, they appear as one
        single order for a volume equal to their total sum.
        Returns sample-data/order-book.json
        The bids array is sorted by price in descending order.
        The asks array is sorted by price in ascending order.
        """
        return self.client.fetch_l2_order_book(asset.symbol)

    def fetch_public_trades(self, asset):
        """Returns list of most recent trades for a particular symbol"""
        return self.client.fetch_trades(asset.symbol)

    def fetch_my_trades(self, asset, since, limit, params=None):
        """Returns list of most recent trades for a particular symbol"""
        params = self.get_default_params_if_none(params)
        return self.client.fetch_my_trades(asset.symbol, since, limit, params)

    def fetch_ticker(self, asset):
        return self.client.fetch_ticker(asset.symbol)

    def fetch_tickers(self):
        """Fetch all tickers at once"""
        return self.client.fetch_tickers()

    def fetch_balance(self):
        """Returns dict in format of sample-data/account_balance"""
        return Balance.from_dict(self.client.fetch_balance())

    def create_limit_buy_order(self, asset, quantity, price, params=None):
        params = self.get_default_params_if_none(params)
        return self.client.create_limit_buy_order(
            asset.symbol, quantity, price, params)

    def create_limit_sell_order(self, asset, quantity, price, params=None):
        return self.client.create_limit_sell_order(
            asset.symbol, quantity, price, params)

    def create_market_buy_order(self, asset, quantity, params=None):
        params = self.get_default_params_if_none(params)
        return self.client.create_market_buy_order(
            asset.symbol, quantity, params)

    def create_market_sell_order(self, asset, quantity, params=None):
        params = self.get_default_params_if_none(params)
        return self.client.create_market_sell_order(
            asset.symbol, quantity, params)

    def cancel_order(self, order_id, asset=None, params=None):
        """
        https://github.com/ccxt/ccxt/wiki/Manual#cancelling-orders"""
        params = self.get_default_params_if_none(params)
        return self.client.cancel_order(order_id)

    def fetch_order(self, order_id, symbol=None, params=None):
        """https://github.com/ccxt/ccxt/wiki/Manual#orders"""
        params = self.get_default_params_if_none(params)
        return self.client.fetch_order(order_id, symbol, params)

    def fetch_orders(self, asset, since=None, limit=None, params=None):
        params = self.get_default_params_if_none(params)
        return self.client.fetch_orders(asset.symbol, since, limit, params)

    def fetch_open_orders(self, asset, since=None, limit=None, params=None):
        params = self.get_default_params_if_none(params)
        return self.client.fetch_open_orders(
            asset.symbol, since, limit, params)

    def fetch_closed_orders(self, asset, since=None, limit=None, params=None):
        params = self.get_default_params_if_none(params)
        return self.client.fetch_closed_orders(
            asset.symbol, since, limit, params)

    def deposit(self, asset):
        return NotImplemented

    def withdraw(self, symbol, quantity, address, params=None):
        params = self.get_default_params_if_none(params)
        return NotImplemented

    @property
    def timeframes(self):
        return self.client.timeframes

    def calculate_fee(self, asset, type, side, quantity,
                      price, taker_or_maker='taker', params=None):
        params = self.get_default_params_if_none(params)
        return self.client.calculate_fee(asset.symbol, type, side,
            quantity, price, taker_or_maker, params)


class PaperExchange(Exchange):
    def __init__(self, id_, config):
        super().__init__(id_, config)
        self.balance = config['balance']
        self.data_provider = config['data_provider']
        self.orders = []
        self.commissions = []

    # Exchange Data Provider

    def get_markets(self):
        return self.data_provider.get_markets()

    def fetch_ohlcv(self, asset, timeframe):
        return self.data_provider.fetch_ohlcv(asset, timeframe)

    def fetch_order_book(self, asset):
        return self.data_provider.fetch_order_book(asset)

    def fetch_ticker(self, asset):
        return self.data_provider.fetch_ticker(asset)

    @property
    def timeframes(self):
        return self.data_provider.timeframes

    def fetch_public_trades(self, asset):
        """Returns list of most recent trades for a particular symbol"""
        return self.data_provider.fetch_public_trades(asset)

    # Paper trading methods

    def fetch_my_trades(self, asset, since, limit, params=None):
        """Returns list of most recent trades for a particular symbol"""
        # TODO: Implement
        return NotImplemented

    def fetch_balance(self):
        """Returns dict in the format of sample-data/account_balance"""
        return self.balance

    def create_limit_buy_order(self, asset, quantity, price):
        return self._create_order(asset, quantity, price, OrderType.LIMIT_BUY)

    def create_limit_sell_order(self, asset, quantity, price):
        return self._create_order(asset, quantity, price, OrderType.LIMIT_SELL)

    def create_market_buy_order(self, asset, quantity):
        # Getting next market price
        # TODO: Decide if we should use the ticker
        #       or the orderbook for market Price
        # if we use orderbook, consider using the calculate_market_price method
        price = self.fetch_ticker(asset)['ask']
        return self._create_order(asset, quantity, price, OrderType.MARKET_BUY)

    def create_market_sell_order(self, asset, quantity):
        # Getting next market price
        # TODO: Decide if we should use the ticker
        #       or the orderbook for market Price
        # if we use orderbook, consider using the calculate_market_price method
        price = self.fetch_ticker(asset)['bid']
        return self._create_order(asset, quantity, price, OrderType.MARKET_SELL)

    def cancel_order(self, order_id):
        # TODO: Implement this when we have pending orders
        return NotImplemented

    def fetch_order(self, order_id, symbol=None):
        for order in self.orders:
            if order.id == order_id:
                return order
        return None

    def fetch_orders(self, asset):
        return self.orders

    def fetch_open_orders(self, asset):
        open_orders = []
        for order in self.orders:
            if order.status == OrderStatus.OPEN:
                open_orders.append(order)
        return open_orders

    def fetch_closed_orders(self, asset):
        open_orders = []
        for order in self.orders:
            if order.status == OrderStatus.CLOSED:
                open_orders.append(order)
        return open_orders

    def deposit(self, asset):
        return NotImplemented
    def withdraw(self, asset, quantity, wallet):
        return NotImplemented
    def calculate_fee(self):
        return NotImplemented
    def order_on_margin(self, price):
        return NotImplemented

    def _create_order(self, asset, quantity, price, order_type):
        """
        Helper method to create orders based on type
        Checks if balance is sufficient, creates Order object
        and calls methods to update balance (_open_order, _fill_order
        Returns Order Dictionary (for CCXT consistency)
        """
        assert quantity != 0 and price != 0
        if not self.balance.is_balance_sufficient(asset, quantity, price, order_type):
            print("Balance is not sufficient to create order!")
            return None
        # TODO: update Order class to have a update_filled_quantity method
        # TODO: update Order class to have a trades (partially filled orders)
        order = Order(self.id, asset, price, quantity,
                order_type, self._make_order_id())
        order.set_status(OrderStatus.CREATED)
        self.orders.append(order)
        # TODO: Implement pending/Open order phase
        order = self._fill_order(order)
        return order.to_dict() # for consistency with CCXT client response

    def _fill_order(self, order):
        # TODO: set the filled time/canceled time, opened time etc somewhere?
        # TODO: change to request_fill_order based on volume
        # TODO: write a cleaner fill order that doesnt need to check order type
        # TODO: handle pending orders, where "used" is also updated
        # For example, when I place a limit order that doesn't get filled
        # my Quote currency total value doesn't change, but its "used" amount does

        base = order.asset.base
        quote = order.asset.quote
        if order.order_type in BUY_ORDER_TYPES:
            self.balance.update(
                currency=quote,
                delta_free=-(order.price * order.quantity),
                delta_used=0.0)
            self.balance.update(
                currency=base,
                delta_free=order.quantity,
                delta_used=0.0)

        elif order.order_type in SELL_ORDER_TYPES:
            self.balance.update(
                currency=quote,
                delta_free=(order.price * order.quantity),
                delta_used=0.0)
            self.balance.update(
                currency=base,
                delta_free=-order.quantity,
                delta_used=0.0)

        order.set_status(OrderStatus.FILLED)
        order.filled_quantity = order.quantity
        return order


    def _make_order_id(self):
        return uuid.uuid4().hex


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
        'verbose':False,
    },
    c.PAPER: {
        'data_provider': CCXTExchange(c.BINANCE, {}),
        'balance': Balance()
    }
}

def load_exchange(id_, config=None):
    """
    exchange_id: ['poloniex', 'simulate', 'gdax']
    c.EX
    """
    if id_ not in EXCHANGE_CONFIGS.keys():
        raise NotImplemented

    if config is None:
        config = EXCHANGE_CONFIGS.get(id_)

    if id_ == c.PAPER:
        return PaperExchange(id_, config)

    return CCXTExchange(id_, config)
