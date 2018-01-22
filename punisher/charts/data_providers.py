import sys
import time
import threading

import pandas as pd
import numpy as np

import punisher.config as cfg
import punisher.constants as c
from punisher.portfolio.asset import Asset
from punisher.feeds.ohlcv_feed import OHLCVData
from punisher.feeds.ohlcv_feed import get_col_name
from punisher.trading import coins
from punisher.trading.record import Record
from punisher.utils.dates import date_to_str


class ChartDataProvider():
    def __init__(self, refresh_sec=None):
        self.refresh_sec = refresh_sec
        self.thread = None

    def initialize(self):
        if self.refresh_sec is not None:
            self.thread = threading.Thread(target=self._update)
            self.thread.start()

    def update(self):
        return NotImplemented

    def _update(self):
        while True:
            print("Refreshing data")
            self.update()
            time.sleep(self.refresh_sec)


class RecordChartDataProvider():
    def __init__(self, root_dir, refresh_sec=5, t_minus=sys.maxsize):
        self.root_dir = root_dir
        self.refresh_sec = refresh_sec
        self.t_minus = t_minus
        self.thread = threading.Thread(target=self.update)
        self.record = Record.load(self.root_dir)

    def initialize(self):
        self.thread.start()

    def get_time(self):
        return self.get_ohlcv().get('utc')

    def get_symbols(self):
        return self.record.portfolio.symbols

    def get_config(self):
        return self.record.config

    def get_ohlcv(self, quote_currency):
        if abs(self.t_minus) >= len(self.record.ohlcv):
            data = OHLCVData(self.record.ohlcv.copy())
        else:
            data = OHLCVData(self.record.ohlcv.iloc[-self.t_minus:].copy())
        assets = self.get_assets()
        ex_ids = self.get_exchange_ids()
        for ex_id in ex_ids:
            for asset in assets:
                if asset.quote != quote_currency:
                    for col in ['open','high','low','close']:
                        ex_rate = self.get_exchange_rate(
                            col, data, asset, ex_id, quote_currency)
                        col_name = get_col_name(col, asset.symbol, ex_id)
                        data.ohlcv_df[col_name] *= ex_rate
        return data

    def get_exchange_rate(self, col, data, asset, ex_id, new_quote):
        # TODO: Refactor this. It's confusing and there is a better way
        # The goal is to be able to view any currency in terms of any other
        # 'quote' currency. Typically the cash currency is BTC, and everything
        # is quoted as such ETH/BTC, LTC/BTC. But it's also useful to see things
        # in terms of USD. Challenge is, not all exchanges support USD (some
        # support USDT, others neither). So we need to try for both.. Ugh.
        if asset.quote == new_quote:
            return 1.0
        if asset.base == new_quote:
            return 1.0
        middleman_asset = self.get_middleman_asset(asset, ex_id, new_quote)
        middleman_price = data.col(col, middleman_asset.symbol, ex_id)
        return middleman_price

    def get_middleman_asset(self, asset, ex_id, new_quote):
        middleman_asset = Asset(asset.quote, new_quote)
        if middleman_asset not in self.get_assets(ex_id):
            if new_quote == coins.USD:
                middleman_asset = Asset(asset.quote, coins.USDT)
            elif new_quote == coins.USDT:
                middleman_asset = Asset(asset.quote, coins.USD)
            if middleman_asset not in self.get_assets(ex_id):
                raise Exception(("No matching quote currency to compute" +
                                 "rate: {:s}, {:s}, {:s}").format(asset.symbol,
                                 ex_id, new_quote))
        return middleman_asset

    def get_assets(self, exchange_id=None):
        cols = ([col for col in self.record.ohlcv.columns
                 if col not in ['epoch', 'utc']])
        symbols = set()
        for col in cols:
            field,symbol,ex_id = col.split('_')
            if exchange_id is None or exchange_id == ex_id:
                symbols.add(symbol)
        return [Asset.from_symbol(sym) for sym in symbols]

    def get_exchange_ids(self):
        cols = ([col for col in self.record.ohlcv.columns
                 if col not in ['epoch', 'utc']])
        ids = set()
        for col in cols:
            field,symbol,ex_id = col.split('_')
            ids.add(ex_id)
        return list(ids)

    def get_quote_currencies(self):
        currencies = set()
        for asset in self.get_assets():
            currencies.add(asset.quote)
        return currencies

    def get_base_currencies(self):
        currencies = set()
        for asset in self.get_assets():
            currencies.add(asset.base)
        return currencies

    def get_positions(self):
        positions = self.record.portfolio.positions
        return pd.DataFrame([p.to_dict() for p in positions])

    def get_positions_dct(self):
        positions = self.record.portfolio.positions
        dct = [p.to_dict() for p in positions]
        return dct

    def get_performance(self):
        return self.record.portfolio.perf

    def get_exchange_rates(self, base, quote, exchange_id):
        asset = Asset(base, quote)
        return self.get_ohlcv(quote).col(
            'close', asset.symbol, exchange_id)

    def get_pnl(self, quote_currency, exchange_id):
        periods = self.record.portfolio.perf.periods
        if quote_currency == coins.BTC:
            ex_rates = np.array([1.0 for p in periods])
        else:
            ex_rates = self.get_exchange_rates(
                coins.BTC, quote_currency, exchange_id)
        assert len(ex_rates) == len(periods)
        df = pd.DataFrame([
            [p['end_time'], p['pnl']] for p in periods
        ], columns=['utc','pnl'])
        df['pnl'] *= ex_rates
        return df

    def get_returns(self, quote_currency, exchange_id):
        periods = self.record.portfolio.perf.periods
        if quote_currency == coins.BTC:
            ex_rates = np.array([1.0 for p in periods])
        else:
            ex_rates = self.get_exchange_rates(
                coins.BTC, quote_currency, exchange_id)
        assert len(ex_rates) == len(periods)
        start_cash = self.record.portfolio.starting_cash * ex_rates[0]
        df = pd.DataFrame([
            [p['end_time'], p['pnl']] for p in periods],
                columns=['utc','returns'])
        df['returns'] *= ex_rates / start_cash
        return df

    def get_balance(self):
        columns = ['coin', 'free', 'used', 'total']
        balance = self.record.balance
        dct = balance.to_dict()
        return pd.DataFrame(
            data=[
                [c, dct[c]['free'], dct[c]['used'], dct[c]['total']]
                for c in balance.currencies],
            columns=columns
        )

    def get_balance_dct(self):
        coins = self.record.balance.currencies
        dct = self.record.balance.to_dict()
        return [{
            'coin':c, 'free':dct[c]['free'],
            'used':dct[c]['used'], 'total':dct[c]['total']
        } for c in coins]

    def get_orders(self):
        columns = [
            'created', 'exchange', 'symbol', 'type',
            'price', 'quantity', 'filled', 'status'
        ]
        data = [
            [o.created_time, o.exchange_id, o.asset.symbol,
             o.order_type.name, o.price, o.quantity, o.filled_quantity,
             o.status.name] for o in self.record.orders.values()
        ]
        return pd.DataFrame(data=data, columns=columns)

    def get_orders_dct(self):
        return [{
            'created': date_to_str(o.created_time),
            'exchange': o.exchange_id,
            'symbol': o.asset.symbol,
            'type': o.order_type.name,
            'price': o.price,
            'quantity': o.quantity,
            'filled': o.filled_quantity,
            'status': o.status.name
            } for o in self.record.orders.values()
        ]

    def get_orders_hist(self):
        raise NotImplemented

    def get_metrics(self):
        return self.record.metrics

    def update(self):
        while True:
            print("Refreshing data")
            self.record = Record.load(self.root_dir)
            time.sleep(self.refresh_sec)



class OHLCVChartDataProvider(ChartDataProvider):
    def __init__(self, feed, refresh_sec=5, t_minus=sys.maxsize):
        super().__init__(refresh_sec)
        self.feed = feed
        self.t_minus = t_minus
        self.ohlcv = {}

    def initialize(self):
        super().initialize()
        self.feed.initialize()
        # Optionally include some history
        # self.ohlcv = self.feed.history(t_minus=100)

    def get_symbols(self):
        return ['ETH/BTC','LTC/BTC']

    def get_next(self):
        """
        Returns dictionary:
            {'close': 0.077,
             'high': 0.0773,
             'low': 0.0771,
             'open': 0.0772,
             'utc': Timestamp('2018-01-08 22:22:00'),
             'volume': 222.514}
        """
        return self.feed.next().to_dict()

    def get_all(self):
        """Returns Dataframe"""
        return self.feed.history()

    def update(self):
        self.feed.update()
