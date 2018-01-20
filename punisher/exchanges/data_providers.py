import abc
import numpy as np

from punisher.utils.dates import utc_to_epoch

supported_timeframes = { '1m': 1, '5m': 5, '30m': 30 }


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


class FeedExchangeDataProvider(ExchangeDataProvider):
    def __init__(self, feed, start=None, end=None):
        super().__init__()
        self.feed = feed
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

    def fetch_ohlcv(self, asset, timeframe):
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
        latest = self.feed.history().row(-1)
        return {
            'symbol': asset.symbol,
            'info': {},
            'timestamp': utc_to_epoch(latest['utc']),
            'datetime': latest['utc'],
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



class CCXTExchangeDataProvider(ExchangeDataProvider):
    def __init__(self, exchange):
        super().__init__()
        self.exchange = exchange

    def get_markets(self):
        return self.exchange.get_markets()

    def fetch_ohlcv(self, asset, timeframe):
        return self.exchange.fetch_ohlcv(asset, timeframe)

    def fetch_order_book(self, asset):
        return self.exchange.fetch_order_book(asset)

    def fetch_public_trades(self, asset):
        return self.exchange.fetch_public_trades(asset)

    def fetch_ticker(self, asset):
        return self.exchange.fetch_ticker(asset)

    @property
    def timeframes(self):
        return self.exchange.timeframes
