import abc
import numpy as np

from datetime import datetime
from punisher.utils.dates import utc_to_epoch

supported_timeframes = { '1m': 1, '5m': 5, '15m': 900, '30m': 1800 }


class ExchangeDataProvider(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

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

    @abc.abstractmethod
    def timeframes(self):
        pass

    @abc.abstractmethod
    def cash_coins(self):
        pass

    @abc.abstractmethod
    def get_time(self):
        pass


class FeedExchangeDataProvider(ExchangeDataProvider):
    def __init__(self, feed, ex_id, start=None, end=None):
        super().__init__()
        self.feed = feed
        self.ex_id = ex_id
        self.start = None
        self.end = None

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

    def fetch_ohlcv(self, asset, timeframe, start_utc):
        #TODO: Currently ignores start time
        return self.feed.history()

    def fetch_order_book(self, asset):
        order_book = {
            'bids': [],
            'asks': [],
            'timestamp': None,
            'datetime': None
        }
        return order_book

    def fetch_public_trades(self, asset):
        trades = []
        return trades

    def fetch_ticker(self, asset):
        history = self.feed.history(t_minus=1)
        open_ = history.get('open', asset.symbol, self.ex_id, idx=-1)
        close = history.get('close', asset.symbol, self.ex_id, idx=-1)
        low = history.get('low', asset.symbol, self.ex_id, idx=-1)
        high = history.get('high', asset.symbol, self.ex_id, idx=-1)
        volume = history.get('volume', asset.symbol, self.ex_id, idx=-1)
        utc = history.get('utc')
        return {
            'symbol': asset.symbol,
            'info': {},
            'timestamp': utc_to_epoch(utc),
            'datetime': utc,
            'high': open_,
            'low': low,
            'bid': close, # faking with close
            'ask': close, # faking with close
            'vwap': None, #volumn weighted price
            'open': open_,
            'first': open_,
            'last': close,
            'change': None, #(percentage change),
            'average': np.mean([open_, close]), #TODO: No idea what this means
            'baseVolume': volume, #(volume of base currency),
            #TODO: should be based on weighted average price
            'quoteVolume': volume * np.mean([open_, close]),
        }

    def get_time(self):
        return self.feed.history(1).get('utc')
        #return self.feed.peek().get('utc')

    @property
    def timeframes(self):
        return supported_timeframes

    @property
    def cash_coins(self):
        return self.feed.cash_coins


class CCXTExchangeDataProvider(ExchangeDataProvider):
    def __init__(self, exchange):
        super().__init__()
        self.exchange = exchange

    def get_markets(self):
        return self.exchange.get_markets()

    def fetch_ohlcv(self, asset, timeframe, start_utc):
        return self.exchange.fetch_ohlcv(asset, timeframe, start_utc)

    def fetch_order_book(self, asset):
        return self.exchange.fetch_order_book(asset)

    def fetch_public_trades(self, asset):
        return self.exchange.fetch_public_trades(asset)

    def fetch_ticker(self, asset):
        return self.exchange.fetch_ticker(asset)

    def get_time(self):
        return datetime.utcnow()

    @property
    def timeframes(self):
        return self.exchange.timeframes

    @property
    def cash_coins(self):
        return self.exchange.cash_coins
