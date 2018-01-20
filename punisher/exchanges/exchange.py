import abc
import ccxt
import uuid
from datetime import datetime
from copy import deepcopy

import ccxt

import punisher.constants as c
import punisher.config as cfg
from punisher.portfolio.asset import Asset
from punisher.portfolio.balance import Balance, BalanceType
from punisher.trading.order import Order, ExchangeOrder
from punisher.trading.order import OrderType, OrderStatus
from punisher.trading import order_manager
from punisher.utils.dates import str_to_date

from .data_providers import CCXTExchangeDataProvider
from .data_providers import FeedExchangeDataProvider


EXCHANGE_CLIENTS = {
    c.BINANCE: ccxt.binance,
    c.POLONIEX: ccxt.poloniex,
    c.GDAX: ccxt.gdax,
}

class Exchange(metaclass=abc.ABCMeta):
    def __init__(self, ex_id):
        self.id = ex_id

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
    def get_bid_ask_spread(order_book):
        bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None
        spread = (ask - bid) if (bid and ask) else None
        return { 'bid': bid, 'ask': ask, 'spread': spread }

    @abc.abstractmethod
    def calculate_fee(self):
        pass

    def is_balance_sufficient(self, asset, quantity, price, order_type):
        return self.fetch_balance().is_balance_sufficient(
            asset, quantity, price, order_type)

    def get_default_params_if_none(self, params):
        return {} if params is None else params


class CCXTExchange(Exchange):
    def __init__(self, ex_id, config):
        # Removing super here in favor of init because
        # http://bit.ly/2qJ9RAP
        Exchange.__init__(self, ex_id)
        self.config = config
        self.client = EXCHANGE_CLIENTS[ex_id](config)

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

    def fetch_order_book(self, asset, params=None):
        """
        https://github.com/ccxt/ccxt/wiki/Manual#order-book--mnrket-depth
        Most common level of aggregation where order volumes are grouped
        by price. If two orders have the same price, they appear as one
        single order for a volume equal to their total sum.
        Returns sample-data/order-book.json
        The bids array is sorted by price in descending order.
        The asks array is sorted by price in ascending order.
        """
        params = self.get_default_params_if_none(params)
        return self.client.fetch_l2_order_book(asset.symbol, params)

    def fetch_public_trades(self, asset):
        """Returns list of most recent trades for a particular symbol"""
        return self.client.fetch_trades(asset.symbol)

    def fetch_my_trades(self, asset, since=None, limit=None, params=None):
        """Returns list of most recent trades for a particular symbol"""
        params = self.get_default_params_if_none(params)
        return self.client.fetch_my_trades(asset.symbol, since, limit, params)

    def fetch_order_trades(self, order_id, asset):
        trades = []
        all_trades = self.fetch_my_trades(asset)
        for trade in all_trades:
            if trade['order'] == order_id:
                trades.append(trade)
        return trades

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
        response = self.client.create_limit_buy_order(
            asset.symbol, quantity, price, params)
        return self.fetch_order(response['id'], asset)

    def create_limit_sell_order(self, asset, quantity, price, params=None):
        print(asset.symbol, quantity, price)
        params = self.get_default_params_if_none(params)
        response = self.client.create_limit_sell_order(
            asset.symbol, quantity, price, params)
        return self.fetch_order(response['id'], asset)

    def create_market_buy_order(self, asset, quantity, params=None):
        params = self.get_default_params_if_none(params)
        response = self.client.create_market_buy_order(
            asset.symbol, quantity, params)
        return self.fetch_order(response['id'], asset)

    def create_market_sell_order(self, asset, quantity, params=None):
        params = self.get_default_params_if_none(params)
        response =  self.client.create_market_sell_order(
            asset.symbol, quantity, params)
        return self.fetch_order(response['id'], asset)

    def cancel_order(self, order_id, asset, params=None):
        """https://github.com/ccxt/ccxt/wiki/Manual#cancelling-orders"""
        params = self.get_default_params_if_none(params)
        return self.client.cancel_order(order_id, asset.symbol)

    def fetch_order(self, order_id, asset, params=None):
        """https://github.com/ccxt/ccxt/wiki/Manual#orders"""
        params = self.get_default_params_if_none(params)
        response = self.client.fetch_order(order_id, asset.symbol, params)
        return self._build_order(response)

    def fetch_orders(self, asset, since=None, limit=None, params=None):
        params = self.get_default_params_if_none(params)
        response = self.client.fetch_orders(asset.symbol, since, limit, params)
        return self._build_orders(response)

    def fetch_open_orders(self, asset, since=None, limit=None, params=None):
        params = self.get_default_params_if_none(params)
        response =  self.client.fetch_open_orders(
            asset.symbol, since, limit, params)
        return self._build_orders(response)

    def fetch_closed_orders(self, asset, since=None, limit=None, params=None):
        params = self.get_default_params_if_none(params)
        response = self.client.fetch_closed_orders(
            asset.symbol, since, limit, params)
        return self._build_orders(response)

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

    def calculate_order_price(self, total_quantity, trades):
        avg_price = 0.0
        for trade in trades:
            trade_qty = trade['amount']
            trade_cost = trade['cost']
            trade_price = trade['price']
            trade_feed = trade['fee']
            avg_price += (trade_qty / total_quantity) * trade_price
        return avg_price

    def calculate_filled_time(self, trades):
        max_time = None
        for trade in trades:
            filled_time = str_to_date(trade['datetime'])
            if max_time is None or filled_time > max_time:
                max_time = filled_time
        return max_time

    def _build_orders(self, orders_dct):
        orders = []
        for order in orders_dct:
            orders.append(self._build_order(order))
        return orders

    def _build_order(self, order_dct):
        # TODO: Add Fees and commissions (using trades)
        print("ORDER Input", order_dct)
        order_dct['status'] = self._get_order_status(order_dct)
        order_dct['exchange_id'] = self.id
        order = ExchangeOrder.from_dict(order_dct)
        order.trades = self.fetch_order_trades(
            order.ex_order_id, order.asset)

        if order.status == OrderStatus.FILLED:
            order.filled_time = self.calculate_filled_time(order.trades)
            order.price = self.calculate_order_price(
                order.filled_quantity, order.trades)

        print("Order Output", order)
        return order

    def _get_order_status(self, order_dct):
        # TODO: Only aware of 2 statuses - What about pending / failed?
        status = order_dct['status'].upper()
        assert status in ['OPEN', 'CLOSED', 'CANCELED']
        if status == 'CLOSED':
            if order_dct['amount'] == order_dct['filled']:
                return OrderStatus.FILLED.name
            else:
                raise Exception("Not sure what this CLOSED is", order_dct)
        elif status == 'OPEN':
            return OrderStatus.OPEN.name
        elif status == 'CANCELED':
            return OrderStatus.CANCELED.name
        raise Exception("Order status not found", status)

    def __repr__(self):
        return 'CCXTExchange({:s})'.format(self.id)


class PaperExchange(Exchange):
    def __init__(self, ex_id, balance, data_provider):
        super().__init__(ex_id)
        self.balance = balance
        self.data_provider = data_provider
        self.orders = []
        self.commissions = []

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

    def fetch_my_trades(self, asset, since=None, limit=None, params=None):
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
        price = self.fetch_ticker(asset)['ask']
        return self._create_order(asset, quantity, price, OrderType.MARKET_BUY)

    def create_market_sell_order(self, asset, quantity):
        price = self.fetch_ticker(asset)['bid']
        return self._create_order(asset, quantity, price, OrderType.MARKET_SELL)

    def cancel_order(self, order_id):
        # TODO: Implement this when we have pending orders
        return NotImplemented

    def fetch_order(self, order_id, asset):
        """Asset Required for CCXT"""
        for order in self.orders:
            if order.ex_order_id == order_id:
                return order
        return None

    def fetch_orders(self, asset):
        orders = []
        for order in self.orders:
            if order.asset.id == asset.id:
                orders.append(order)
        return orders

    def fetch_open_orders(self, asset):
        open_orders = []
        for order in self.orders:
            if order.status == OrderStatus.OPEN and order.asset.id == asset.id:
                open_orders.append(order)
        return open_orders

    def fetch_closed_orders(self, asset):
        open_orders = []
        for order in self.orders:
            if order.status == OrderStatus.OPEN and order.asset.id == asset.id:
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
        assert quantity != 0 and price != 0
        order = ExchangeOrder.from_dict({
            'id': self.make_order_id(),
            'exchange_id': self.id,
            'symbol': asset.symbol,
            'amount': quantity,
            'price': price,
            'filled': 0.0,
            'side': order_type.side,
            'type': order_type.type,
            'status': OrderStatus.OPEN.name,
            'datetime': datetime.utcnow().isoformat()
        })

        if not self.balance.is_balance_sufficient(
            asset=asset,
            quantity=quantity,
            price=price,
            order_type=order_type):

            # TODO: Implement our own InsufficientFunds
            raise ccxt.errors.InsufficientFunds((
                'Insufficient funds to place order for asset {:s} of' +
                ' cost: {:.5f}. {:s} balance is: {}. {:s} balance is {}').format(
                asset.symbol, quantity*price, asset.quote,
                self.balance.get(asset.quote)[BalanceType.FREE],
                asset.base, self.balance.get(asset.base)[BalanceType.FREE])
            )

        order = self._fill_order(order)
        self.orders.append(order)

        return order

    def _fill_order(self, order):
        # TODO: set the filled time/canceled time, opened time etc somewhere?
        # TODO: change to request_fill_order based on volume
        # TODO: write a cleaner fill order that doesnt need to check order type
        # TODO: handle pending orders, where "used" is also updated
        # For example, when I place a limit order that doesn't get filled
        # my Quote currency total value doesn't change,
        # but its "used" amount does
        self.balance.update_by_order(order.asset, order.quantity,
                                     order.price, order.order_type)
        order.filled_quantity = order.quantity
        order.filled_time = datetime.utcnow()
        order.status = OrderStatus.FILLED
        return order

    def make_order_id(self):
        return uuid.uuid4().hex

    def __repr__(self):
        return 'PaperExchange({:s})'.format(self.id)


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
        'data_provider_exchange_id': cfg.DEFAULT_EXCHANGE_ID,
        'balance': c.DEFAULT_BALANCE
    }
}

def load_feed_based_paper_exchange(balance, feed, feed_ex_id=c.PAPER):
    balance = deepcopy(balance)
    data_provider = FeedExchangeDataProvider(feed, feed_ex_id)
    return PaperExchange(c.PAPER, balance, data_provider)

def load_ccxt_based_paper_exchange(balance, exchange_id):
    balance = deepcopy(balance)
    exchange = load_exchange(exchange_id)
    data_provider = CCXTExchangeDataProvider(exchange)
    return PaperExchange(c.PAPER, balance, data_provider)

def load_exchange(ex_id, config=None):
    if ex_id not in EXCHANGE_CONFIGS.keys():
        raise NotImplemented

    if config is None:
        config = deepcopy(EXCHANGE_CONFIGS.get(ex_id))

    if ex_id == c.PAPER:
        dp_exchange_id = config['data_provider_exchange_id']
        balance = Balance.from_dict(config['balance'])
        return load_ccxt_based_paper_exchange(balance, dp_exchange_id)

    return CCXTExchange(ex_id, config)
