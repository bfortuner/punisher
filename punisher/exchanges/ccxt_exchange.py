import uuid
from datetime import datetime
from copy import deepcopy

import ccxt

from punisher.portfolio.balance import Balance, BalanceType
from punisher.trading.order import Order, ExchangeOrder
from punisher.trading.order import OrderType, OrderStatus
from punisher.trading import order_manager
from punisher.utils.dates import str_to_date
from punisher.utils.dates import utc_to_epoch

from .exchange import Exchange
from .ex_cfg import *


class CCXTExchange(Exchange):
    def __init__(self, ex_id, config):
        super().__init__(ex_id)
        self.config = config
        self.client = EXCHANGE_CLIENTS[ex_id](config)

    def get_markets(self):
        if self.client.markets is None:
            return self.client.load_markets(reload=True)
        return self.client.markets

    def fetch_ohlcv(self, asset, timeframe, start_utc):
        """
        Returns OHLCV for the symbol based on the time_period
        ex. fetch_ohlcv(btcusd, 1d)
        To see all timeframes for an exchange use timeframes property
        when hasFetchTickers is True as well
        """
        assert self.client.hasFetchOHLCV
        # CCXT expects milliseconds since epoch for 'since'
        epoch_ms = utc_to_epoch(start_utc) * 1000
        return self.client.fetch_ohlcv(asset.symbol, timeframe.id, since=epoch_ms)

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

    @property
    def timeframes(self):
        return self.client.timeframes

    @property
    def cash_coins(self):
        return self.config['cash_coins']

    @property
    def usd_coin(self):
        return self.config['usd_coin']

    def __repr__(self):
        return 'CCXTExchange({:s})'.format(self.id)
