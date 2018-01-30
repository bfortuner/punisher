import pytest
from copy import copy, deepcopy
from datetime import datetime

from punisher import constants as c
from punisher.exchanges import (
    load_exchange, ex_cfg, load_feed_based_paper_exchange)
from punisher.portfolio.portfolio import Portfolio
from punisher.portfolio.performance import PerformanceTracker
from punisher.portfolio.balance import Balance
from punisher.portfolio.position import Position
from punisher.portfolio.asset import Asset
from punisher.trading import coins
import punisher.feeds.ohlcv_feed as ohlcv_feed
from punisher.utils.dates import Timeframe


@pytest.fixture(scope="class")
def ccxtexchange():
   return load_exchange(ex_cfg.BINANCE)

@pytest.fixture(scope="class")
def paperexchange(balance, asset):
    exchange_id = ex_cfg.BINANCE
    assets = [asset]
    balance = deepcopy(balance)
    timeframe = Timeframe.ONE_MIN

    # Ensuring we have data for the paper exchange
    start = datetime(year=2018, month=1, day=1, hour=0)
    end = datetime(year=2018, month=1, day=2, hour=0)
    data_exchange = load_exchange(exchange_id)
    ohlcv_feed.download_ohlcv(
        [data_exchange], assets, timeframe, start, end)

    feed = ohlcv_feed.OHLCVFileFeed(
        exchange_ids=[exchange_id],
        assets=assets,
        timeframe=timeframe,
        start=None,
        end=None
    )
    feed.next()
    ex = load_feed_based_paper_exchange(
        balance, feed, exchange_id)
    return ex

@pytest.fixture(scope="class")
def perf_tracker():
    return PerformanceTracker(
        starting_cash=0.0,
        timeframe=Timeframe.ONE_MIN
    )

@pytest.fixture(scope="class")
def portfolio(perf_tracker, balance):
    return Portfolio(
        cash_currency=coins.USDT,
        starting_balance=deepcopy(balance),
        perf_tracker=perf_tracker, # option to override, otherwise default
        positions=None # option to override with existing positions
    )

@pytest.fixture(scope="class")
def balance():
    return Balance(
        cash_currency=coins.USDT,
        starting_cash=0.0
    )

@pytest.fixture(scope="class")
def asset():
    return Asset.from_symbol("BTC/USDT")

@pytest.fixture(scope="class")
def position(asset):
    return Position(
        asset=asset,
        quantity=0.0,
        cost_price=0.0
    )
