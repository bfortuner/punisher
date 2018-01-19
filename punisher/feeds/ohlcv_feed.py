import os
import datetime
import pandas as pd

import punisher.config as cfg
import punisher.constants as c
from punisher.portfolio.asset import Asset
from punisher.utils.dates import get_time_range
from punisher.utils.dates import epoch_to_utc, utc_to_epoch
from punisher.utils.dates import str_to_date


class OHLCVData():
    def __init__(self, ohlcv_df):
        self.ohlcv_df = ohlcv_df

    def get(self, field, asset=None, ex_id=None, idx=0):
        col_name = self._get_col_name(field, asset, ex_id)
        return self.ohlcv_df[col_name].iloc[idx]

    def col(self, field, asset=None, ex_id=None):
        col_name = self._get_col_name(field, asset, ex_id)
        return self.ohlcv_df[col_name].values

    def row(self, idx):
        row = self.ohlcv_df.iloc[idx]
        return row
        #return row.to_frame().T.to_records()

    def all(self):
        return self.ohlcv_df.to_records()

    def _get_col_name(self, field, asset, ex_id):
        field_str = field
        if asset is not None:
            field_str += '_' + asset.id
        if ex_id is not None:
            field_str += '_' + ex_id
        return field_str

    def __len__(self):
        return len(self.ohlcv_df)


class OHLCVFeed():
    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end
        self.prior_time = None
        self.ohlcv_df = None

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
        data = self.ohlcv_df[self.ohlcv_df.index <= utc_to_epoch(
            self.prior_time)]
        return OHLCVData(data[-t_minus:])

    def peek(self):
        row = self.ohlcv_df[self.ohlcv_df.index > utc_to_epoch(
            self.prior_time)]
        if len(row) > 0:
            return OHLCVData(row.iloc[0].to_frame().T)
        return None

    def next(self, refresh=False):
        if refresh:
            self.end = datetime.datetime.utcnow()
            self.update()
        row = self.ohlcv_df[self.ohlcv_df.index > utc_to_epoch(
            self.prior_time)]
        if len(row) > 0:
            row = row.iloc[0]
            self.prior_time = row['time_utc']
            return OHLCVData(row.to_frame().T)
        print("No data after prior poll:", self.prior_time)
        return None

    def __len__(self):
        return len(self.ohlcv_df)


class OHLCVFileFeed(OHLCVFeed):
    def __init__(self, fpath, start=None, end=None):
        super().__init__(start, end)
        self.fpath = fpath
        self.initialize()

    def initialize(self):
        super().initialize()
        self.update()

    def update(self):
        self.ohlcv_df = load_chart_data_from_file(
            self.fpath, self.prior_time, self.end)


class OHLCVExchangeFeed(OHLCVFeed):
    def __init__(self, exchange, assets, timeframe,
                 start, end=None):
        super().__init__(start, end)
        self.exchange = exchange
        self.assets = assets
        self.period = timeframe.id
        self.initialize()

    def initialize(self):
        super().initialize()
        self.update()

    def next(self, refresh=True):
        return super().next(refresh)

    def update(self):
        self._download(self.prior_time, self.end)
        if len(self.assets) > 1:
            self.ohlcv_df = load_multiple_assets(
                self.exchange.id, self.assets, self.period,
                self.start, self.end)
        else:
            fpath = get_price_data_fpath(
                self.assets[0], self.exchange.id, self.period)
            self.ohlcv_df = load_chart_data_from_file(
                fpath, self.start, self.end)

    def _download(self, start, end):
        download_chart_data(
            self.exchange, self.assets,
            self.period, start, end)


# Helpers

def get_price_data_fpath(asset, exchange_id, period):
    fname = '{:s}_{:s}_{:s}.csv'.format(
        exchange_id, asset.id, str(period))
    return os.path.join(cfg.DATA_DIR, fname)

def fetch_ohlcv_data(exchange, asset, period, start, end=None):
    print("Downloading:", asset.symbol)
    assert period in exchange.timeframes
    end = datetime.datetime.utcnow() if end is None else end
    data = exchange.fetch_ohlcv(asset, period)
    df = make_ohlcv_df(data, start, end)
    print("Downloaded rows:", len(df))
    return df

def fetch_and_save_ohlcv_data(exchange, asset, period, start, end=None):
    df = fetch_ohlcv_data(exchange, asset, period, start, end)
    fpath = get_price_data_fpath(asset, exchange.id, period)
    df.to_csv(fpath, index=True)
    return df

def update_local_ohlcv_data(exchange, asset, period, start, end=None):
    fpath = get_price_data_fpath(asset, exchange.id, period)
    if os.path.exists(fpath):
        df = fetch_ohlcv_data(exchange, asset, period, start, end)
        df = merge_local_csv_feeds(df, fpath)
    else:
        df = fetch_and_save_ohlcv_data(exchange, asset, period, start, end)
    return df

def load_chart_data_from_file(fpath, start=None, end=None):
    df = pd.read_csv(
        fpath, index_col='time_epoch',
        parse_dates=['time_utc'],
        date_parser=str_to_date)
    df.sort_index(inplace=True)
    df = get_time_range(df, start, end)
    return df

def download_chart_data(exchange, assets, period, start, end=None):
    for asset in assets:
        update_local_ohlcv_data(exchange, asset, period, start, end)

def load_multiple_assets(exchange_id, assets, period, start, end=None):
    df = pd.DataFrame()
    for asset in assets:
        fpath = get_price_data_fpath(asset, exchange_id, period)
        data = load_chart_data_from_file(fpath, start, end)
        df[asset.id] = data['close']
    df.dropna(inplace=True)
    df['time_utc'] = [epoch_to_utc(t) for t in df.index]
    return df

def make_ohlcv_df(data, start=None, end=None):
    df = pd.DataFrame(data, columns=c.OHLCV_COLUMNS)
    df['time_epoch'] = df['time_epoch'] // 1000 # ccxt includes millis
    df['time_utc'] = [epoch_to_utc(t) for t in df['time_epoch']]
    df.set_index('time_epoch', inplace=True)
    df.sort_index(inplace=True)
    df = get_time_range(df, start, end)
    return df

def merge_local_csv_feeds(new_data, fpath):
    cur_df = pd.read_csv(
        fpath, index_col='time_epoch',
        parse_dates=['time_utc'],
        date_parser=str_to_date)
    new_df = pd.DataFrame(new_data)
    cur_df = pd.concat([cur_df, new_df])
    cur_df = cur_df[~cur_df.index.duplicated(keep='last')]
    cur_df.to_csv(fpath, index=True)
    return cur_df


EXCHANGE_FEED = 'EXCHANGE_FEED'
CSV_FEED = 'CSV_FEED'
DATA_FEEDS = {
    EXCHANGE_FEED: OHLCVExchangeFeed,
    CSV_FEED: OHLCVFileFeed
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
