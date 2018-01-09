import abc

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
        self.data_feed = data_feed.initialize()

    # Exchange Data Provider

    def get_markets(self):
        return self.data_provider.get_markets()

    def fetch_ohlcv(self, asset, timeframe):
        return self.data_provider.fetch_ohlcv(asset, timeframe)

    def fetch_order_book(self, asset):
        return self.data_provider.fetch_order_book(asset)

    def fetch_public_trades(self, asset):
        """Returns list of most recent trades for a particular symbol"""
        return self.data_provider.fetch_public_trades(asset)

    def fetch_ticker(self, asset):
        return self.data_provider.fetch_ticker(asset)

    @property
    def timeframes(self):
        return self.data_provider.timeframes
