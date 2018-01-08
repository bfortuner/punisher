import abc
import ccxt
import constants as c
import config as cfg
import uuid

from portfolio.asset import Asset
from portfolio.balance import (BalanceType, DEFAULT_BALANCE,
                              add_asset_to_balance, update_balance)
from trading.order import Order, OrderType
from trading.order import BUY_ORDER_TYPES, SELL_ORDER_TYPE


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
    c.PAPER: {
        'data_provider_name': c.BACKTEST_DATA_PROVIDER_NAME,
        'data_provider_config': None
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

    # TODO: add historical paper trading data provider
    if id_ == c.PAPER:
        data_provider_name = config.get("data_provider_name")

        # If data provider is a CCXT Exchange
        if data_provider_name in EXCHANGE_CONFIGS.keys() and (
            data_provider_name != c.PAPER):

            data_provider_config = EXCHANGE_CONFIGS.get(data_provider_name)
            data_provider = CCXTExchange(
                data_provider_name, data_provider_config)

        else: # Data Provider is BACKTEST_DATA_PROVIDER
            # TODO: implement backtest data provider
            data_provider_config = config.get("data_provider_config")
            data_provider = None

        return PaperExchange(id_, config, data_provider)

    return CCXTExchange(id_, config)


class Exchange(metaclass=abc.ABCMeta):

    def __init__(self, id_, config):
        self.id = id_
        self.config = config
        self.exchange_balance = DEFAULT_BALANCE

    @abc.abstractmethod
    def get_markets(self):
        pass

    @abc.abstractmethod
    def fetch_order_book(self, asset):
        pass

    @abc.abstractmethod
    def fetch_public_trades(self, asset):
        pass

    @abc.abstractmethod
    def fetch_my_trades(self, asset):
        pass

    @abc.abstractmethod
    def fetch_ticker(self, asset):
        pass

    @abc.abstractmethod
    def fetch_balance(self):
        pass

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
    def fetch_order_book(self, asset):
        pass

    @abc.abstractmethod
    def fetch_ohlcv(self, asset):
        pass

    @abc.abstractmethod
    def fetch_order(self, order_id, asset=None, params=None):
        pass

    @abc.abstractmethod
    def fetch_orders(self, asset, since=None, limit=None, params=None):
        pass

    @abc.abstractmethod
    def fetch_open_orders(self, asset, since=None, limit=None, params=None):
        pass

    @abc.abstractmethod
    def fetch_closed_orders(self, asset, since=None, limit=None, params=None):
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

    def _ensure_asset_in_balance(self, asset):
        # add base and quote symbols to balance if necessary
        # TODO: think about another way to ensure the
        #       balance has each asset we need
        if asset.base not in self.exchange_balance:
            self.exchange_balance = add_asset_to_balance(
                asset.base, 0, 0, self.exchange_balance)
        if asset.quote not in self.exchange_balance:
            self.exchange_balance = add_asset_to_balance(
                asset.quote, 0, 0, self.exchange_balance)

    def is_balance_sufficient(self, asset, quantity, price, order_type):

        self._ensure_asset_in_balance(asset)

        # Check if the quantity needed to purchase/sell is
        # less/more than the quantity in your available balance
        if order_type in buy_order_types():
            return price * quantity <= self.exchange_balance.get(
                asset.quote).get(BalanceType.AVAILABLE)
        elif order_type in sell_order_types():
            return quantity >= self.exchange_balance.get(
                asset.base).get(BalanceType.AVAILABLE)
        else:
            print("Order type {} not supported".format(order_type))
            return False

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
        return self.fetch_l2_order_book(asset.symbol)

    def fetch_public_trades(self, asset):
        """Returns list of most recent trades for a particular symbol"""
        return self.client.fetch_trades(asset.symbol)

    def fetch_my_trades(self, asset, since, limit, params=None):
        """Returns list of most recent trades for a particular symbol"""
        return self.client.fetch_my_trades(asset.symbol, since, limit, params)

    def fetch_ticker(self, asset):
        return self.client.fetch_ticker(asset.symbol)

    def fetch_tickers(self):
        """Fetch all tickers at once"""
        return self.client.fetch_tickers()

    def fetch_balance(self):
        """Returns json in the format of sample-data/account_balance"""
        return self.client.fetch_balance()

    def create_limit_buy_order(self, asset, quantity, price, params=None):
        return self.client.create_limit_buy_order(
            asset.symbol, quantity, price, params)

    def create_limit_sell_order(self, asset, quantity, price, params=None):
        return self.client.create_limit_sell_order(
            asset.symbol, quantity, price, params)

    def create_market_buy_order(self, asset, quantity, params=None):
        return self.client.create_market_buy_order(
            asset.symbol, quantity, params)

    def create_market_sell_order(self, asset, quantity, params=None):
        return self.client.create_market_sell_order(
            asset.symbol, quantity, params)

    def cancel_order(self, order_id, asset=None, params=None):
        """
        https://github.com/ccxt/ccxt/wiki/Manual#cancelling-orders"""
        return self.client.cancel_order(order_id)

    def fetch_order(self, order_id, asset=None, params=None):
        """https://github.com/ccxt/ccxt/wiki/Manual#orders"""
        params = self.get_default_params_if_none(params)
        return self.client.fetch_order(order_id, symbol, params)

    def fetch_orders(self, asset, since=None, limit=None, params=None):
        return self.client.fetch_orders(asset.symbol, since, limit, params)

    def fetch_open_orders(self, asset, since=None, limit=None, params=None):
        return self.client.fetch_open_orders(
            asset.symbol, since, limit, params)

    def fetch_closed_orders(self, asset, since=None, limit=None, params=None):
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
        return self.client.calculate_fee(asset.symbol, type, side,
            quantity, price, taker_or_maker, params)


class PaperExchange(Exchange):
    def __init__(self, id_, config, data_provider):
        super().__init__(id_, config)
        self.data_provider = data_provider
        self.orders = []
        self.commissions = []

    def get_markets(self):
        return self.data_provider.get_markets()

    def fetch_ohlcv(self, asset, timeframe):
        return self.data_provider.fetch_ohlcv(asset.symbol, timeframe)

    def fetch_order_book(self, asset):
        return self.data_provider.fetch_l2_order_book(asset.symbol)

    def fetch_public_trades(self, asset):
        """Returns list of most recent trades for a particular symbol"""
        return self.data_provider.fetch_trades(asset.symbol)

    def fetch_my_trades(self, asset, since, limit, params=None):
        """Returns list of most recent trades for a particular symbol"""
        return self.data_provider.fetch_my_trades(
            asset.symbol, since, limit, params)

    def fetch_ticker(self, asset):
        return self.data_provider.fetch_ticker(asset.symbol)

    def fetch_tickers(self):
        """Fetch all tickers at once"""
        return self.data_provider.fetch_tickers()

    # Paper trading methods

    def fetch_balance(self):
        """Returns json in the format of sample-data/account_balance"""
        return self.exchange_balance

    def create_limit_buy_order(self, asset, quantity, price):
        return self._create_order(asset, quantity, price, OrderType.LIMIT_BUY)

    def create_limit_sell_order(self, asset, quantity, price):
        return self._create_order(asset, quantity, price, OrderType.LIMIT_SELL)

    def create_market_buy_order(self, asset, quantity):
        # Getting next market price
        # TODO: Decide if we should use the ticker
        #       or the orderbook for market Price
        # if we use orderbook, consider using the calculate_market_price method
        price = self.get_ticker(asset).get("ask")
        return self._create_order(asset, quantity, price, OrderType.MARKET_BUY)

    def create_market_sell_order(self, asset, quantity):
        # Getting next market price
        # TODO: Decide if we should use the ticker
        #       or the orderbook for market Price
        # if we use orderbook, consider using the calculate_market_price method
        price = self.get_ticker(asset).get("bid")
        return self._create_order(asset, quantity, price, OrderType.MARKET_SELL)

    def cancel_order(self, order_id):
        # TODO: Implement this when we have pending orders
        return NotImplemented

    def fetch_order(self, order_id):
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
        Returns Order object
        """
        if not is_balance_sufficient(asset, quantity, price, order_type):
            print("Balance is not sufficient to create order!")
            return None
        # TODO: update Order class to have a update_filled_quantity method
        # TODO: update Order class to have a trades (partially filled orders)

        order = Order(self.id_, asset, price, quantity,
                order_type, self._make_order_id())
        order.set_status(OrderType.CREATED)
        self.orders.append(order)
        # TODO: Implement pending/Open order phase
        order = self._fill_order(order)
        return order

    def _fill_order(self, order):
        # TODO: set the filled time/canceled time, opened time etc somewhere?
        # TODO: change to request_fill_order based on volume
        # TODO: write a cleaner fill order that doesnt need to check order type

        if order.order_type in order():
            # subtract from the quote asset's balance
            self.balance.update(
                order.asset.quote, -(order.price * order.quantity),
                0.0, self.exchange_balance)

            # add to the base asset's balance
            self.balance.update(
                order.asset.base, order.quantity,
                0.0, self.exchange_balance)

        elif order_type in sell_order_types():
            # add to the quote asset's balance
            self.balance.update(
                order.asset.quote, (order.price * order.quantity),
                0.0, self.exchange_balance)

            # subtract from the base asset's balance
            self.balance.update_currency(
                order.asset.base, -order.quantity,
                0.0, self.exchange_balance)

        order.set_status(OrderType.FILLED)
        order.filled_quantity = order.quantity
        return order

    def _make_order_id(self):
        return uuid.uuid4().hex
