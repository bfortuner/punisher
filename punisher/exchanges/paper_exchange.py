import uuid
from datetime import datetime
from copy import deepcopy

import ccxt

from punisher.portfolio.asset import Asset
from punisher.portfolio.balance import Balance, BalanceType
from punisher.trading.order import Order, ExchangeOrder
from punisher.trading.order import OrderType, OrderStatus
from punisher.trading import order_manager
from punisher.trading.trade import Trade
from punisher.utils.dates import str_to_date, date_to_str
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

    @property
    def cash_coins(self):
        return self.data_provider.cash_coins

    @property
    def usd_coin(self):
        # Since we control paper exchange, we'll handle the conversion
        # of USDT --> USD where needed. This way for backtesting users
        # don't need to care about USD/USDT.
        return self.config['usd_coin']

    def fetch_public_trades(self, asset):
        """Returns list of most recent trades for a particular symbol"""
        return self.data_provider.fetch_public_trades(asset)

    def fetch_my_trades(self, asset, since=None, limit=None, params=None):
        """Returns list of most recent trades for a particular symbol"""
        # TODO: implement since and limit
        trades = []
        for order in orders:
            if order.asset == asset:
                trades.append(order.trades)
        return trades

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

    def calculate_fee(self, asset, type, side, quantity,
                      price, taker_or_maker=None, params=None):
        # TODO: Implement this
        # taker = market order
        # maker = limit order
        cost = abs(quantity) * price
        fee_rate = self._get_fee_rate(asset, taker_or_maker)
        fee = cost * fee_rate
        return fee

    def order_on_margin(self, price):
        return NotImplemented

    def _create_order(self, asset, quantity, price, order_type):
        assert quantity != 0 and price != 0
        print("TIME", self.data_provider.get_time())
        order = ExchangeOrder.from_dict({
            'id': self.make_order_id(),
            'exchange_id': self.id,
            'symbol': asset.symbol,
            'amount': quantity,
            'price': price,
            'filled': 0.0,
            'side': order_type.side,
            'type': order_type.type,
            'status': OrderStatus.CREATED.name,
            'datetime': date_to_str(self.data_provider.get_time())
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

        self.balance.update_with_created_order(order)
        # Now that we have created the order, update it's status to open
        # since it is in the exchange
        order.status = OrderStatus.OPEN
        order = self._fill_order(order)
        self.orders.append(order)

        return order

    def _fill_order(self, order):
        # TODO: implement slippage

        fee = self.calculate_fee(
                asset=order.asset,
                type=order.order_type,
                side=order.order_type.side,
                quantity=order.quantity,
                price=order.price,
                taker_or_maker=None
            )

        trade = Trade(
            trade_id=None,
            exchange_id=self.id,
            exchange_order_id=order.ex_order_id,
            asset=order.asset,
            price=order.price,
            quantity=order.quantity,
            trade_time=self.data_provider.get_time(),
            side=order.order_type.side,
            fee=fee
        )

        self.balance.update_with_trade(trade)

        order.trades.append(trade)
        order.filled_quantity = trade.quantity
        order.filled_time = self.data_provider.get_time()
        order.status = OrderStatus.FILLED
        return order

    def _get_fee_rate(self, asset, taker_or_maker):
        # TODO: do this crap
        return 0.0

    def make_order_id(self):
        return uuid.uuid4().hex

    def __repr__(self):
        return 'PaperExchange({:s})'.format(self.id)
