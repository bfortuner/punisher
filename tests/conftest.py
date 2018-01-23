import pytest

from punisher import constants as c
from punisher.exchanges.exchange import load_exchange
from punisher.portfolio.portfolio import Portfolio
from punisher.portfolio.performance import PerformanceTracker
from punisher.portfolio.balance import Balance
from punisher.portfolio.position import Position
from punisher.portfolio.asset import Asset
from punisher.trading import coins
from punisher.utils.dates import Timeframe


@pytest.fixture(scope="class")
def ccxtexchange():
   return load_exchange(ex_cfg.BINANCE)

@pytest.fixture(scope="class")
def paperexchange():
    return load_exchange(ex_cfg.PAPER)

@pytest.fixture(scope="class")
def perf_tracker():
    return PerformanceTracker(
        starting_cash=0.0,
        timeframe=Timeframe.ONE_MIN
    )

@pytest.fixture(scope="class")
def portfolio(perf_tracker):
    return Portfolio(
        cash_currency=coins.BTC,
        starting_cash=0.0,
        perf_tracker=perf_tracker, # option to override, otherwise default
        positions=None # option to override with existing positions
    )

@pytest.fixture(scope="class")
def balance():
    return Balance(
        cash_currency=coins.BTC,
        starting_cash=0.0
    )

@pytest.fixture(scope="class")
def asset():
    return Asset.from_symbol("BTC/USD")

@pytest.fixture(scope="class")
def position(asset):
    return Position(
        asset=asset,
        quantity=0.0,
        cost_price=0.0
    )
