import uuid
from datetime import datetime
from copy import deepcopy

import ccxt

from punisher.portfolio.asset import Asset
from punisher.portfolio.balance import Balance, BalanceType
from punisher.trading.order import Order, ExchangeOrder
from punisher.trading.order import OrderType, OrderStatus
from punisher.trading import order_manager
from punisher.utils.dates import str_to_date
from punisher.utils.dates import utc_to_epoch

from .data_providers import CCXTExchangeDataProvider
from .data_providers import FeedExchangeDataProvider
from .exchange import Exchange
from .ex_cfg import *


class PaperExchange(Exchange):
    def __init__(self, ex_id, balance, data_provider):
        super().__init__(ex_id)
        self.balance = balance
        self.data_provider = data_provider
        self.orders = []
        self.commissions = []

    def get_markets(self):
        return self.data_provider.get_markets()

    def fetch_ohlcv(self, asset, timeframe, start_utc):
        return self.data_provider.fetch_ohlcv(asset, timeframe, start_utc)

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
