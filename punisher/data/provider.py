import abc
import numpy as np
from enum import Enum

from punisher.utils.dates import utc_to_epoch

supported_timeframes = { '1m': 1, '5m': 5, '30m': 30 }


class DataProvider(metaclass=abc.ABCMeta):
    def __init__(self, id_, config):
        self.id = id_
        self.config = config

    @abc.abstractmethod
    def get_markets(self):
        pass

    @abc.abstractmethod
    def fetch_ohlcv(self, asset):
        pass

    @abc.abstractmethod
    def fetch_order_book(self, asset):
        pass

    @abc.abstractmethod
    def fetch_public_trades(self, asset):
        pass

    @abc.abstractmethod
    def fetch_ticker(self, asset):
        pass

    def to_json(self):
        return { "id": self.id }


class PaperExchangeDataProvider(DataProvider):
    def __init__(self, data_feed, id_="backtest_data_provider", config=None):
        super().__init__(id_, config)
        # TODO: figure out a way to have all the data rows for each
        #       currency instead of just one
        self.data_feed = data_feed
        # current row data
        # time_epoch	open	high	low	close	volume	time_utc

    def get_markets(self):
        markets = []
        market = {
            'id': None,
            'symbol': None,
            'base': None,
            'quote': None,
            'precision': {
                'price': None,
                'amount': None,
                'cost': None,
            },
            'limits': {
                'amount': {
                    'min': None,
                    'max': None,
                },
                'price': {},
                'cost': {}
            }
        }
        markets.append(market)
        return markets

    def fetch_ohlcv(self, asset, timeframe=None):
        all_rows = self.data_feed.history().tail()
        return all_rows

    def fetch_order_book(self, asset):
        # TODO: actually get historical order book data
        order_book = {
            'bids': [],
            'asks': [],
            'timestamp': None,
            'datetime': None
        }
        return order_book

    def fetch_public_trades(self, asset):
        """Returns list of most recent trades for a particular symbol"""
        trades = []
        return trades

    def fetch_ticker(self, asset):
        latest = self.fetch_ohlcv(asset).iloc[-1]
        return {
            'symbol': asset.symbol,
            'info': {},
            'timestamp': utc_to_epoch(latest['time_utc']),
            'datetime': latest['time_utc'],
            'high': latest['open'],
            'low': latest['low'],
            'bid': latest['close'], # faking with close
            'ask': latest['close'], # faking with close
            'vwap': None, #volumn weighted price
            'open': latest['open'],
            'first': latest['open'],
            'last': latest['close'],
            'change': None, #(percentage change),
            'average': np.mean([latest['open'], latest['close']]), #TODO: No idea what this means
            'baseVolume': latest['volume'], #(volume of base currency),
            #TODO: should be based on weighted average price
            'quoteVolume': latest['volume'] * np.mean([latest['open'], latest['close']]),
        }

    @property
    def timeframes(self):
        return supported_timeframes
