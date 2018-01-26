import pytest
from copy import copy, deepcopy

from punisher import constants as c
from punisher.exchanges import load_exchange, ex_cfg
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
def paperexchange(balance):
    ex = load_exchange(ex_cfg.PAPER)
    ex.balance = deepcopy(balance)
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
        cash_currency=coins.USD,
        starting_balance=deepcopy(balance),
        perf_tracker=perf_tracker, # option to override, otherwise default
        positions=None # option to override with existing positions
    )

@pytest.fixture(scope="class")
def balance():
    return Balance(
        cash_currency=coins.USD,
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
