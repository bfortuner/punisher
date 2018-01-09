import abc
from enum import Enum

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


class PaperExchangeDataProvider(DataProvider):
    def __init__(self, data_feed, id_="backtest_data_provider", config=None):
        super().__init__(id_, config)
        # TODO: figure out a way to have all the data rows for each
        #       currency instead of just one
        self.data_feed = data_feed
        self.data_feed.initialize()
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

    def fetch_ohlcv(self, asset, timeframe):
        # TODO: only doing minute data for now until we figure out how to
        #       update the data_feed
        assert timeframe in supported_timeframes.keys()
        t_minus = supported_timeframes.get(timeframe)
        if t_minus == 1:
            rows = [self.data_feed.next()]
        else:
            # TODO: fix this
            rows = self.data_feed.history(t_minus)
            rows.append(self.data_feed.next())

        res = []
        ohlcv = []
        # Building response starting with most recent ohlcv data
        for row in rows[::-1]:
            ohlcv.append(row['time_utc'])
            ohlcv.append(row['open'])
            ohlcv.append(row['high'])
            ohlcv.append(row['low'])
            ohlcv.append(row['close'])
            ohlcv.append(row['volume'])
            res.append(ohlcv)
        return res

    def fetch_order_book(self, asset):
        # TODO: actually get historical order book data
        order_book = {
            'bids': [],
            'asks': [],
            'timestamp': self.data_feed.next()['time_utc'],
            'datetime': None
        }
        return order_book

    def fetch_public_trades(self, asset):
        """Returns list of most recent trades for a particular symbol"""
        trades = []
        return trades

    def fetch_ticker(self, asset):
        ticker = {}
        return ticker

    @property
    def timeframes(self):
        return supported_timeframes
