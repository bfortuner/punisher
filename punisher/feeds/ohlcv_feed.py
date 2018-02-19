import os
import datetime
import pandas as pd
from pathlib import Path

import punisher.config as cfg
import punisher.constants as c
from punisher.exchanges import ex_cfg
from punisher.portfolio.asset import Asset
from punisher.trading import coins
from punisher.utils.dates import get_time_range
from punisher.utils.dates import epoch_to_utc, utc_to_epoch
from punisher.utils.dates import str_to_date


OHLCV_COLUMNS = ['epoch', 'open', 'high', 'low', 'close', 'volume']
# Open - Bid/Ask? at beginning of time period (quoted in cash)
# High - Highest Bid/Ask? during time period (quoted in cash)
# Low - Lowest Bid/Ask? during time period (quoted in cash)
# Close - Bid/Ask? at end of time period (quoted in cash)
# Volume - Quantity of base coin traded during time period (quoted in base)

class OHLCVData():
    def __init__(self, ohlcv_df):
        self.ohlcv_df = ohlcv_df

    def get(self, field, symbol=None, ex_id=None, idx=0):
        col_name = l_name(field, symbol, ex_id)
        return self.ohlcv_df[col_name].iloc[idx]

    def col(self, field, symbol=None, ex_id=None):
        col_name = get_col_name(field, symbol, ex_id)
        return self.ohlcv_df[col_name].values

    def row(self, idx):
        return self.ohlcv_df.iloc[idx]

    def cash_value(self, col, cash_currency):
        pass

    @property
    def df(self):
        return self.ohlcv_df

    @property
    def cash_coins(self):
        cash = set()
        columns = [c for c in self.ohlcv_df.columns if c not in ['utc', 'epoch']]
        for col in columns:
            field,symbol,ex_id = col.split('_')
            asset = Asset.from_symbol(symbol)
            if asset.quote in [coins.USD, coins.USDT]:
                cash.add(coins.USD)
            else:
                cash.add(asset.quote)
        return cash

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
        self.ex_ids = [ex.id for ex in exchanges]
        self.assets = assets
        self.timeframe = timeframe
        self.benchmark = benchmark
        self.initialize()

    def initialize(self):
        super().initialize()
        self.init_benchmarks()
        print("START", self.start)
        print("END", self.end)
        self._download(self.start, self.end, update=False)
        self.ohlcv_df = load_multiple_assets(
            self.ex_ids, self.assets, self.timeframe,
            self.start, self.end)

    def init_benchmarks(self):
        if self.benchmark:
            for ex in self.exchanges:
                asset = get_benchmark_asset(ex)
                self.assets.append(asset)

    def next(self, refresh=True):
        return super().next(refresh)

    def update(self):
        if self.ohlcv_df.empty:
            most_recent_data_time = self.start
        else:
            most_recent_data_time = self.ohlcv_df.tail(1).iloc[0].get('utc')
        self._download(
            most_recent_data_time, self.end, update=True)
        self.ohlcv_df = load_multiple_assets(
            self.ex_ids, self.assets, self.timeframe,
            self.start, self.end)

    def _download(self, start, end, update=True):
        for ex in self.exchanges:
            for asset in self.assets:
                if is_asset_supported(ex, asset):
                    download_ohlcv(
                        [ex], [asset], self.timeframe,
                        start, end, update
                    )


# Helpers

def get_usd_coin(ex_id):
    return ex_cfg.EXCHANGE_CONFIGS[ex_id]['usd_coin']

def get_exchange_rate(df, quote_coin, new_cash_coin, ex_id):
    assert coins.is_cash(new_cash_coin)

    if coins.is_usd(new_cash_coin):
        new_cash_coin = get_usd_coin(ex_id)
    if coins.is_usd(quote_coin):
        quote_coin = get_usd_coin(ex_id)
    if quote_coin == new_cash_coin:
        return pd.Series([1.0 for i in range(len(df))]).values

    new_cash_symbol = coins.get_symbol(quote_coin, new_cash_coin)
    cash_col_name = get_col_name('close', new_cash_symbol, ex_id)
    if cash_col_name in df.columns:
        return df[cash_col_name].values
    else:
        new_cash_symbol = coins.get_symbol(new_cash_coin, quote_coin)
        cash_col_name = get_col_name('close', new_cash_symbol, ex_id)
        return pd.Series(1.0 / df[cash_col_name]).values

def get_cash_value(df, field, asset, ex_id, cash_coin):
    assert coins.is_cash(cash_coin)
    assert field in ['open', 'high', 'low', 'close']
    #print("Cash value of", asset.symbol, "in", cash_coin, "on exchange", ex_id)

    if coins.is_usd(cash_coin):
        cash_coin = get_usd_coin(ex_id)
    if coins.is_usd(asset.quote):
        asset.quote = get_usd_coin(ex_id)
    cash_symbol = coins.get_symbol(asset.quote, cash_coin)

    col_name = get_col_name(field, asset.symbol, ex_id)
    col = df[col_name]

    if asset.quote == cash_coin:
        return col.values
    if asset.base == cash_coin:
        return col.values

    cash_col_name = get_col_name(field, cash_symbol, ex_id)
    cash_col = df[cash_col_name]
    return (col * cash_col).values

def is_asset_supported(exchange, asset):
    markets = exchange.get_markets()
    return asset.symbol in markets

def get_benchmark_asset(exchange):
    BTC_USD = Asset(coins.BTC, coins.USD)
    BTC_USDT = Asset(coins.BTC, coins.USDT)
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

def get_ohlcv_fname(asset, exchange_id, timeframe):
    fname = '{:s}_{:s}_{:s}.csv'.format(
        exchange_id, asset.id, timeframe.id)
    return fname

def get_ohlcv_fpath(asset, exchange_id, timeframe, outdir=cfg.DATA_DIR):
    fname = get_ohlcv_fname(asset, exchange_id, timeframe)
    return Path(outdir, fname)

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

def download_ohlcv(exchanges, assets, timeframe, start, end=None, update=False):
    for ex in exchanges:
        for asset in assets:
            if update:
                _ = update_local_asset_cache(ex, asset, timeframe, start, end)
            else:
                _ = fetch_and_save_asset(ex, asset, timeframe, start, end)

def load_ohlcv(ex_id, asset, timeframe, start=None, end=None):
    fpath = get_ohlcv_fpath(asset, ex_id, timeframe)
    return load_asset(fpath, start, end)

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
                print("Fpath does not exist: {:s}".format(str(fpath)))
    # TODO: Is this okay? How to fill in missing values? How to handle them?
    # df.dropna(inplace=True)
    df['utc'] = [epoch_to_utc(t) for t in df.index]
    return df

def make_asset_df(data, asset, ex_id, start=None, end=None):
    columns = get_ohlcv_columns(asset, ex_id)
    df = pd.DataFrame(data, columns=columns)
    df['epoch'] = df['epoch'] // 1000 # ccxt includes millis
    df['epoch'] = df['epoch'].astype(int)
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

def check_missing_timesteps(df, timestep):
    df = df.sort_values(by='utc')
    start_time = df.iloc[0]['utc']
    end_time = df.iloc[-1]['utc']
    print("Start", start_time)
    print("End", end_time)
    last_time = start_time
    n_missing = 0
    for idx,row in df[1:].iterrows():
        cur_time = row['utc']
        if cur_time != last_time + datetime.timedelta(seconds=timestep):
            print("Expected:", last_time + datetime.timedelta(seconds=timestep),
                  "| Time:", cur_time)
            n_missing += (cur_time - last_time).seconds//timestep
        last_time = cur_time
    return n_missing

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
