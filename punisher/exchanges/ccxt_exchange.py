import uuid
from datetime import datetime
from copy import deepcopy

import ccxt

from punisher.portfolio.balance import Balance, BalanceType
from punisher.trading.order import Order, ExchangeOrder
from punisher.trading.order import OrderType, OrderStatus
from punisher.trading import order_manager
from punisher.trading.trade import Trade
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

    def fetch_raw_order_book(self, asset, limit=1000, level=3):
        """
        https://github.com/ccxt/ccxt/wiki/Manual#order-book--mnrket-depth
        Each exchange has a different parameter for raw order book
        # https://docs.gdax.com/#get-product-order-book
        # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md
        # Is Binance aggregated or raw?
        """
        params = {}
        if self.id == BINANCE:
            params['limit'] = limit
        elif self.id == GDAX:
            params['level'] = level
        return self.client.fetch_order_book(asset.symbol, params)

    def fetch_public_trades(self, asset, start=None, end=None, limit=None):
        """Returns list of trades for a particular symbol"""
        params = {}
        if self.id == POLONIEX:
            params = {
                'start': utc_to_epoch(start) if start is not None else None,
                'end': utc_to_epoch(end) if end is not None else utc_to_epoch(datetime.utcnow())
            }
        start = utc_to_epoch(start)*1000 if start is not None else utc_to_epoch(start)
        response = self.client.fetch_trades(asset.symbol, start, limit, params)
        return self._build_trades(response)

    def fetch_my_trades(self, asset, start=None, limit=None, params=None):
        """Returns list of most recent trades for a particular symbol"""
        params = self.get_default_params_if_none(params)
        start = utc_to_epoch(start)*1000 if start is not None else start
        response = self.client.fetch_my_trades(asset.symbol, since, limit, params)
        return self._build_trades(response)

    def fetch_order_trades(self, order_id, asset):
        trades = []
        all_trades = self.fetch_my_trades(asset)
        for trade in all_trades:
            if trade.exchange_order_id == order_id:
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

    def calculate_filled_time(self, trades):
        max_time = None
        for trade in trades:
            filled_time = trade.trade_time
            if max_time is None or filled_time > max_time:
                max_time = filled_time
        return max_time

    def _build_trades(self, trades_list):
        trades = []
        for trade in trades_list:
            trades.append(self._build_trade(trade))
        return trades

    def _build_trade(self, trade_dct):
        trade_dct['exchange_id'] = self.id
        trade_dct['quantity'] = trade_dct['amount']
        trade_dct['trade_time'] = trade_dct['datetime']
        if 'fee' in trade_dct and trade_dct['fee'] is not None:
            trade_dct['fee'] = trade_dct['fee'].get("cost", None)
        else:
            trade_dct['fee'] = 0.0
        return Trade.from_dict(trade_dct)

    def _build_orders(self, orders_dct):
        orders = []
        for order in orders_dct:
            orders.append(self._build_order(order))
        return orders

    def _build_order(self, order_dct):
        # TODO: Add Fees and commissions (using trades)
        order_dct['status'] = self._get_order_status(order_dct)
        order_dct['exchange_id'] = self.id
        order = ExchangeOrder.from_dict(order_dct)
        order.trades = self.fetch_order_trades(
            order.ex_order_id, order.asset)
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

    def is_active_symbol(self, markets, symbol):
        return ('.' not in symbol) and (
            ('active' not in markets[symbol])
            or (markets[symbol]['active']))

    @property
    def symbols(self):
        markets = self.get_markets()
        symbols = self.client.symbols
        return [s for s in symbols if self.is_active_symbol(markets, s)]

    @property
    def timeframes(self):
        return self.client.timeframes

    @property
    def cash_coins(self):
        return self.config['cash_coins']

    @property
    def usd_coin(self):
        return self.config['usd_coin']

    @property
    def rate_limit(self):
        return self.client.rate_limit / 1000

    def __repr__(self):
        return 'CCXTExchange({:s})'.format(self.id)
