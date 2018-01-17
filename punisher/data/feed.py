import datetime

import punisher.utils.dates as date_utils
from . import ohlcv


class DataFeed():
    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end
        self.prior_time = None
        self.feed = None

    def initialize(self):
        if self.start is None:
            self.start = datetime.datetime(1, 1, 1, 1, 1)
        self.prior_time = self.start - datetime.timedelta(minutes=1)

    def update(self):
        pass

    def history(self, t_minus=0):
        """Return t_minus rows from feed
        Which should represent the latest dates seen by Strategy
        """
        data = self.feed[self.feed.index <= date_utils.utc_to_epoch(
            self.prior_time)]
        return data[-t_minus:]

    def peek(self):
        data = self.history()
        if len(data) > 0:
            return data.iloc[-1]
        return None

    def next(self, refresh=False):
        if refresh:
            self.end = datetime.datetime.utcnow()
            self.update()
        data = self.feed[self.feed.index > date_utils.utc_to_epoch(
            self.prior_time)]
        if len(data) > 0:
            # iloc[0] returns a series, which acts like a dictionary
            row = data.iloc[0]
            self.prior_time = row['time_utc']
            return row
        print("No data after prior poll:", self.prior_time)
        return None

    def __len__(self):
        return len(self.feed)


class CSVDataFeed(DataFeed):
    def __init__(self, fpath, start=None, end=None):
        super().__init__(start, end)
        self.fpath = fpath

    def initialize(self):
        super().initialize()
        self.update()

    def update(self):
        self.feed = ohlcv.load_chart_data_from_file(
            self.fpath, self.prior_time, self.end)


class ExchangeDataFeed(DataFeed):
    def __init__(self, exchange, assets, timeframe,
                 start, end=None):
        super().__init__(start, end)
        self.exchange = exchange
        self.assets = assets
        self.period = timeframe.id

    def initialize(self):
        super().initialize()
        self.update()

    def next(self, refresh=True):
        return super().next(refresh)

    def update(self):
        self._download(self.prior_time, self.end)
        if len(self.assets) > 1:
            self.feed = ohlcv.load_multiple_assets(
                self.exchange.id, self.assets, self.period,
                self.start, self.end)
        else:
            fpath = ohlcv.get_price_data_fpath(
                self.assets[0], self.exchange.id, self.period)
            self.feed = ohlcv.load_chart_data_from_file(
                fpath, self.start, self.end)

    def _download(self, start, end):
        ohlcv.download_chart_data(
            self.exchange, self.assets,
            self.period, start, end)


EXCHANGE_FEED = 'EXCHANGE_FEED'
CSV_FEED = 'CSV_FEED'
DATA_FEEDS = {
    EXCHANGE_FEED: ExchangeDataFeed,
    CSV_FEED: CSVDataFeed
}

# TODO remove or refactor this method
def load_feed(name, fpath, assets=None,
              timeframe=None, start=None, end=None):
    assert name in DATA_FEEDS.keys()
    if name == EXCHANGE_FEED:
        return ExchangeDataFeed(
            assets, timeframe,
            fpath, start, end
        )
    return CSVDataFeed(fpath, start, end)
