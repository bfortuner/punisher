import os
import datetime
import pandas as pd

import punisher.config as cfg
import punisher.constants as c
from punisher.portfolio.asset import Asset
from punisher.utils.dates import get_time_range
from punisher.utils.dates import epoch_to_utc, utc_to_epoch
from punisher.utils.dates import str_to_date


<<<<<<< HEAD
OHLCV_COLUMNS = ['epoch', 'open', 'high', 'low', 'close', 'volume']

=======
>>>>>>> 96979db3aba45d2da2ef08c0fb04906c632381dc
class OHLCVData():
    def __init__(self, ohlcv_df):
        self.ohlcv_df = ohlcv_df

    def get(self, field, asset=None, ex_id=None, idx=0):
<<<<<<< HEAD
        col_name = get_col_name(field, asset, ex_id)
        return self.ohlcv_df[col_name].iloc[idx]

    def col(self, field, asset=None, ex_id=None):
        col_name = get_col_name(field, asset, ex_id)
        return self.ohlcv_df[col_name].values

    def row(self, idx):
        return self.ohlcv_df.iloc[idx]
=======
        col_name = self._get_col_name(field, asset, ex_id)
        return self.ohlcv_df[col_name].iloc[idx]

    def col(self, field, asset=None, ex_id=None):
        col_name = self._get_col_name(field, asset, ex_id)
        return self.ohlcv_df[col_name].values

    def row(self, idx):
        row = self.ohlcv_df.iloc[idx]
        return row
        #return row.to_frame().T.to_records()
>>>>>>> 96979db3aba45d2da2ef08c0fb04906c632381dc

    def all(self):
        return self.ohlcv_df.to_records()

<<<<<<< HEAD
=======
    def _get_col_name(self, field, asset, ex_id):
        field_str = field
        if asset is not None:
            field_str += '_' + asset.id
        if ex_id is not None:
            field_str += '_' + ex_id
        return field_str

>>>>>>> 96979db3aba45d2da2ef08c0fb04906c632381dc
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
<<<<<<< HEAD
        if self.end is None:
            self.end = datetime.datetime.utcnow()
=======
>>>>>>> 96979db3aba45d2da2ef08c0fb04906c632381dc
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
<<<<<<< HEAD
            self.prior_time = row['utc']
=======
            self.prior_time = row['time_utc']
>>>>>>> 96979db3aba45d2da2ef08c0fb04906c632381dc
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
<<<<<<< HEAD
        self.ohlcv_df = load_asset(
=======
        self.ohlcv_df = load_chart_data_from_file(
>>>>>>> 96979db3aba45d2da2ef08c0fb04906c632381dc
            self.fpath, self.prior_time, self.end)


class OHLCVExchangeFeed(OHLCVFeed):
<<<<<<< HEAD
    def __init__(self, exchanges, assets, timeframe,
                 start, end=None):
        super().__init__(start, end)
        self.exchanges = exchanges
=======
    def __init__(self, exchange, assets, timeframe,
                 start, end=None):
        super().__init__(start, end)
        self.exchange = exchange
>>>>>>> 96979db3aba45d2da2ef08c0fb04906c632381dc
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
<<<<<<< HEAD
        if len(self.assets) > 1 or len(self.exchanges) > 1:
            ex_ids = [ex.id for ex in self.exchanges]
            self.ohlcv_df = load_multiple_assets(
                ex_ids, self.assets, self.period,
                self.start, self.end)
        else:
            fpath = get_ohlcv_fpath(
                self.assets[0], self.exchanges[0].id, self.period)
            self.ohlcv_df = load_asset(
                fpath, self.start, self.end)

    def _download(self, start, end):
        for exchange in self.exchanges:
            download_ohlcv_data(
                exchange, self.assets,
                self.period, start, end)
=======
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
>>>>>>> 96979db3aba45d2da2ef08c0fb04906c632381dc


# Helpers

<<<<<<< HEAD
def get_col_name(field, asset=None, ex_id=None):
    field_str = field
    if asset is not None:
        field_str += '_' + asset.symbol
    if ex_id is not None:
        field_str += '_' + ex_id
    return field_str

def get_ohlcv_columns(asset, ex_id):
    cols = OHLCV_COLUMNS.copy()
    return [get_col_name(c, asset, ex_id) for c in cols]

def get_ohlcv_fpath(asset, exchange_id, period):
=======
def get_price_data_fpath(asset, exchange_id, period):
>>>>>>> 96979db3aba45d2da2ef08c0fb04906c632381dc
    fname = '{:s}_{:s}_{:s}.csv'.format(
        exchange_id, asset.id, str(period))
    return os.path.join(cfg.DATA_DIR, fname)

<<<<<<< HEAD
def fetch_asset(exchange, asset, period, start, end=None):
=======
def fetch_ohlcv_data(exchange, asset, period, start, end=None):
>>>>>>> 96979db3aba45d2da2ef08c0fb04906c632381dc
    print("Downloading:", asset.symbol)
    assert period in exchange.timeframes
    end = datetime.datetime.utcnow() if end is None else end
    data = exchange.fetch_ohlcv(asset, period)
<<<<<<< HEAD
    df = make_asset_df(data, start, end)
    print("Downloaded rows:", len(df))
    return df

def fetch_and_save_asset(exchange, asset, period, start, end=None):
    df = fetch_asset(exchange, asset, period, start, end)
    fpath = get_ohlcv_fpath(asset, exchange.id, period)
    df.to_csv(fpath, index=True)
    return df

def update_local_asset_cache(exchange, asset, period, start, end=None):
    fpath = get_ohlcv_fpath(asset, exchange.id, period)
    if os.path.exists(fpath):
        df = fetch_asset(exchange, asset, period, start, end)
        df = merge_asset_dfs(df, fpath)
    else:
        df = fetch_and_save_asset(exchange, asset, period, start, end)
    return df

def download_ohlcv_data(exchange, assets, period, start, end=None):
    for asset in assets:
        update_local_asset_cache(exchange, asset, period, start, end)

def load_asset(fpath, start=None, end=None):
    df = pd.read_csv(
        fpath, index_col='epoch',
        parse_dates=['utc'],
=======
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
>>>>>>> 96979db3aba45d2da2ef08c0fb04906c632381dc
        date_parser=str_to_date)
    df.sort_index(inplace=True)
    df = get_time_range(df, start, end)
    return df

<<<<<<< HEAD
def load_multiple_assets(exchange_ids, assets, period, start, end=None):
    df = pd.DataFrame()
    for ex_id in exchange_ids:
        for asset in assets:
            fpath = get_ohlcv_fpath(asset, ex_id, period)
            data = load_asset(fpath, start, end)
            for col in OHLCV_COLUMNS[1:]:
                col_name = get_col_name(col, asset, ex_id)
                df[col_name] = data[col]
                asset_col_name = get_col_name(col, asset)
                if asset_col_name in df:
                    df[asset_col_name] += data[col] / len(exchange_ids)
                else:
                    df[asset_col_name] = data[col] / len(exchange_ids)
    df.dropna(inplace=True)
    df['utc'] = [epoch_to_utc(t) for t in df.index]
    return df

def make_asset_df(data, asset, ex_id, start=None, end=None):
    df = pd.DataFrame(data, columns=c.OHLCV_COLUMNS)
    df['epoch'] = df['epoch'] // 1000 # ccxt includes millis
    df['utc'] = [epoch_to_utc(t) for t in df['epoch']]
    df.set_index('epoch', inplace=True)
=======
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
>>>>>>> 96979db3aba45d2da2ef08c0fb04906c632381dc
    df.sort_index(inplace=True)
    df = get_time_range(df, start, end)
    return df

<<<<<<< HEAD
def merge_asset_dfs(new_data, fpath):
    cur_df = pd.read_csv(
        fpath, index_col='epoch',
        parse_dates=['utc'],
=======
def merge_local_csv_feeds(new_data, fpath):
    cur_df = pd.read_csv(
        fpath, index_col='time_epoch',
        parse_dates=['time_utc'],
>>>>>>> 96979db3aba45d2da2ef08c0fb04906c632381dc
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
