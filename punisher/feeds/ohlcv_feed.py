import os
import datetime
import pandas as pd

import punisher.config as cfg
import punisher.constants as c
from punisher.portfolio.asset import Asset
from punisher.utils.dates import get_time_range
from punisher.utils.dates import epoch_to_utc, utc_to_epoch
from punisher.utils.dates import str_to_date


OHLCV_COLUMNS = ['epoch', 'open', 'high', 'low', 'close', 'volume']

class OHLCVData():
    def __init__(self, ohlcv_df):
        self.ohlcv_df = ohlcv_df

    def get(self, field, symbol=None, ex_id=None, idx=0):
        col_name = get_col_name(field, symbol, ex_id)
        return self.ohlcv_df[col_name].iloc[idx]

    def col(self, field, symbol=None, ex_id=None):
        col_name = get_col_name(field, symbol, ex_id)
        return self.ohlcv_df[col_name].values

    def row(self, idx):
        return self.ohlcv_df.iloc[idx]

    def all(self):
        return self.ohlcv_df.to_records() # TODO: return df instead

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
        if self.end is None:
            self.end = datetime.datetime.utcnow()
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
            self.prior_time = row['utc']
            return OHLCVData(row.to_frame().T)
        print("No data after prior poll:", self.prior_time)
        return None

    def __len__(self):
        return len(self.ohlcv_df)


class OHLCVFileFeed(OHLCVFeed):
    def __init__(self, exchange_ids, assets, timeframe,
                 start=None, end=None):
        super().__init__(start, end)
        self.exchange_ids = exchange_ids
        self.timeframe = timeframe
        self.assets = assets
        self.initialize()

    def initialize(self):
        super().initialize()
        self.update()

    def update(self):
        self.ohlcv_df = load_multiple_assets(
            self.exchange_ids, self.assets, self.timeframe,
            self.start, self.end)


class OHLCVExchangeFeed(OHLCVFeed):
    def __init__(self, exchanges, assets, timeframe,
                 start, end=None, benchmark=True):
        super().__init__(start, end)
        self.exchanges = exchanges
        self.assets = assets
        self.timeframe = timeframe
        self.benchmark = benchmark
        self.initialize()

    def initialize(self):
        super().initialize()
        self.init_benchmarks()
        self.update()

    def init_benchmarks(self):
        if self.benchmark:
            for ex in self.exchanges:
                asset = get_benchmark_asset(ex)
                self.assets.append(asset)

    def next(self, refresh=True):
        return super().next(refresh)

    def update(self):
        self._download(self.prior_time, self.end)
        ex_ids = [ex.id for ex in self.exchanges]
        self.ohlcv_df = load_multiple_assets(
            ex_ids, self.assets, self.timeframe,
            self.start, self.end)

    def _download(self, start, end):
        for ex in self.exchanges:
            for asset in self.assets:
                if is_asset_supported(ex, asset):
                    download_ohlcv([ex], [asset], self.timeframe, start, end)

# Helpers

def is_asset_supported(exchange, asset):
    markets = exchange.get_markets()
    return asset.symbol in markets

def get_benchmark_asset(exchange):
    BTC_USD = Asset(c.BTC, c.USD)
    BTC_USDT = Asset(c.BTC, c.USDT)
    markets = exchange.get_markets()
    if BTC_USD.symbol in markets:
        return BTC_USD
    elif BTC_USDT.symbol in markets:
        return BTC_USDT
    return None

def get_col_name(field, symbol=None, ex_id=None):
    field_str = field
    if symbol is not None:
        field_str += '_' + symbol
    if ex_id is not None:
        field_str += '_' + ex_id
    return field_str

def get_ohlcv_columns(asset, ex_id):
    cols = OHLCV_COLUMNS.copy()
    for i in range(1,len(cols)):
        cols[i] = get_col_name(cols[i], asset.symbol, ex_id)
    return cols

def get_ohlcv_fpath(asset, exchange_id, timeframe):
    fname = '{:s}_{:s}_{:s}.csv'.format(
        exchange_id, asset.id, timeframe.id)
    return os.path.join(cfg.DATA_DIR, fname)

def fetch_asset(exchange, asset, timeframe, start, end=None):
    ## TODO: Some exchanges adhere to limits. For instance BINANCE
    # returns 500 rows, while POLONIEX returns all rows. Additionally
    # exchanges offer different amounts of historical data. We need to
    # update this method to:
    #   1) Inform the user when requested dates are not available
    #   2) Break up large date range into <500 so all exchanges work
    print("Downloading:", asset.symbol)
    assert timeframe.id in exchange.timeframes
    end = datetime.datetime.utcnow() if end is None else end
    data = exchange.fetch_ohlcv(asset, timeframe, start)
    df = make_asset_df(data, asset, exchange.id, start, end)
    print("Downloaded rows:", len(df))
    return df

def fetch_and_save_asset(exchange, asset, timeframe, start, end=None):
    df = fetch_asset(exchange, asset, timeframe, start, end)
    fpath = get_ohlcv_fpath(asset, exchange.id, timeframe)
    df.to_csv(fpath, index=True)
    return df

def update_local_asset_cache(exchange, asset, timeframe, start, end=None):
    fpath = get_ohlcv_fpath(asset, exchange.id, timeframe)
    if os.path.exists(fpath):
        df = fetch_asset(exchange, asset, timeframe, start, end)
        df = merge_asset_dfs(df, fpath)
    else:
        df = fetch_and_save_asset(exchange, asset, timeframe, start, end)
    return df

def download_ohlcv(exchanges, assets, timeframe, start, end=None):
    for ex in exchanges:
        for asset in assets:
            update_local_asset_cache(ex, asset, timeframe, start, end)

def load_asset(fpath, start=None, end=None):
    df = pd.read_csv(
        fpath, index_col='epoch',
        parse_dates=['utc'],
        date_parser=str_to_date)
    df.sort_index(inplace=True)
    df = get_time_range(df, start, end)
    return df

def load_multiple_assets(exchange_ids, assets, timeframe, start, end=None):
    """
    Returns OHLCV dataframe for multiple assets + exchanges
    The data is loaded from previously downloaded files
    If it cannot find a particular file it skips it and keeps going (dangerous)
        Why? Not every exchange supports every asset. This is especially
        important for benchmark assets like USD / USDT.
    Column name syntax = `field_asset_exchange`
    """
    df = pd.DataFrame()
    for ex_id in exchange_ids:
        for asset in assets:
            fpath = get_ohlcv_fpath(asset, ex_id, timeframe)
            if os.path.exists(fpath):
                data = load_asset(fpath, start, end)
                for col in data.columns:
                    df[col] = data[col]
            else:
                print("Fpath does not exist: {:s}. \nJust a heads up.".format(fpath))
    # TODO: Is this okay? How to fill in missing values? How to handle them?
    # df.dropna(inplace=True)
    df['utc'] = [epoch_to_utc(t) for t in df.index]
    return df

def make_asset_df(data, asset, ex_id, start=None, end=None):
    columns = get_ohlcv_columns(asset, ex_id)
    df = pd.DataFrame(data, columns=columns)
    df['epoch'] = df['epoch'] // 1000 # ccxt includes millis
    df['utc'] = [epoch_to_utc(t) for t in df['epoch']]
    df.set_index('epoch', inplace=True)
    df.sort_index(inplace=True)
    df = get_time_range(df, start, end)
    return df

def merge_asset_dfs(new_data, fpath):
    cur_df = pd.read_csv(
        fpath, index_col='epoch',
        parse_dates=['utc'],
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
