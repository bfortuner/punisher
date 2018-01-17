import abc
import ccxt
import uuid
from copy import deepcopy

import punisher.constants as c
import punisher.config as proj_cfg
from punisher.portfolio.asset import Asset
from punisher.portfolio.balance import Balance, BalanceType
from punisher.trading.order import Order, OrderType, OrderStatus
from punisher.trading import order_manager

from .data_providers import CCXTExchangeDataProvider
from .data_providers import FeedExchangeDataProvider


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

    # TODO make this take in an asset instead of a symbol
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

    def __repr__(self):
        return 'CCXTExchange({:s})'.format(self.id)


class PaperExchange(Exchange):
    def __init__(self, id_, config):
        super().__init__(id_, config)
        self.balance = Balance.from_dict(config['balance'])
        # TODO: implement get_data_provider
        self.data_provider = self._get_data_provider(config.get("data_provider"))
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

    # TODO make this take in an asset instead of a symbol
    def fetch_order(self, order_id, symbol=None):
        for order in self.orders:
            if order['id'] == order_id:
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
        if not self.balance.is_balance_sufficient(
            asset, quantity, price, order_type):
            print("Balance is not sufficient to create order!")
            return None
        # TODO: update Order class to have a update_filled_quantity method
        # TODO: update Order class to have a trades (partially filled orders)
        order = Order(self.id, asset, price, quantity,
                order_type)
        order.status = OrderStatus.FILLED.name
        order_dct = self._fill_order(order)
        order_dct['created_time'] = order.created_time.isoformat()
        self.orders.append(order_dct)
        return order_dct # for consistency with CCXT client response

    def _fill_order(self, order):
        # TODO: set the filled time/canceled time, opened time etc somewhere?
        # TODO: change to request_fill_order based on volume
        # TODO: write a cleaner fill order that doesnt need to check order type
        # TODO: handle pending orders, where "used" is also updated
        # For example, when I place a limit order that doesn't get filled
        # my Quote currency total value doesn't change, but its "used" amount does

        base = order.asset.base
        quote = order.asset.quote
        if order.order_type.is_buy():
            self.balance.update(
                currency=quote,
                delta_free=-(order.price * order.quantity),
                delta_used=0.0)
            self.balance.update(
                currency=base,
                delta_free=order.quantity,
                delta_used=0.0)

        elif order.order_type.is_sell():
            self.balance.update(
                currency=quote,
                delta_free=(order.price * order.quantity),
                delta_used=0.0)
            self.balance.update(
                currency=base,
                delta_free=-order.quantity,
                delta_used=0.0)

        # For consistency with CCXT
        return {
            'id': self._make_order_id(),
            'symbol': order.asset.symbol,
            'price': order.price,
            'quantity': order.quantity,
            'type': order.order_type.value['type'],
            'side': order.order_type.value['side'],
            'filled': order.filled_quantity,
            'status': order.status, # TODO: Fix inconsistency w CCXT
            'fee': order.fee
        }

    def _get_data_provider(self, data_provider):
        if data_provider:
            return data_provider
        return CCXTExchange(c.DEFAULT_DATA_PROVIDER_EXCHANGE, {})

    def _make_order_id(self):
        return uuid.uuid4().hex

    def __repr__(self):
        return 'PaperExchange({:s})'.format(self.id)


EXCHANGE_CONFIGS = {
    c.POLONIEX: {
        'apiKey': proj_cfg.POLONIEX_API_KEY,
        'secret': proj_cfg.POLONIEX_API_SECRET_KEY,
    },
    c.GDAX: {
        'apiKey': proj_cfg.GDAX_API_KEY,
        'secret': proj_cfg.GDAX_API_SECRET_KEY,
        'password': proj_cfg.GDAX_PASSPHRASE,
        'verbose':False,
    },
    c.BINANCE: {
        'apiKey': proj_cfg.BINANCE_API_KEY,
        'secret': proj_cfg.BINANCE_API_SECRET_KEY,
        'verbose':False,
    },
    c.PAPER: {
        'data_provider': None,
        'balance': c.DEFAULT_BALANCE
    }
}

def load_feed_based_paper_exchange(balance, feed):
    data_provider = FeedExchangeDataProvider(feed)
    return PaperExchange(c.PAPER, balance, data_provider)

def load_ccxt_based_paper_exchange(balance, exchange_id):
    exchange = load_exchange(exchange_id)
    data_provider = CCXTExchangeDataProvider(exchange)
    return PaperExchange(c.PAPER, balance, data_provider)

def load_exchange(ex_id, config=None):
    if ex_id not in EXCHANGE_CONFIGS.keys():
        raise NotImplemented

    config = deepcopy(EXCHANGE_CONFIGS.get(id_))

    # Add/replace any exchange configs from the input config
    if cfg:
        for key, value in cfg.items():
            config[key] = value

    return CCXTExchange(ex_id, config)
