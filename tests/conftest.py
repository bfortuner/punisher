import pytest
from datetime import datetime

from punisher import constants as c
from punisher.exchanges.exchange import load_exchange
from punisher.portfolio.portfolio import Portfolio
from punisher.portfolio.performance import PerformanceTracker
from punisher.portfolio.balance import Balance
from punisher.portfolio.position import Position
from punisher.portfolio.asset import Asset
from punisher.trading.trade import Trade
from punisher.utils.dates import Timeframe


@pytest.fixture(scope="class")
def ccxtexchange():
   return load_exchange(c.BINANCE)

@pytest.fixture(scope="class")
def paperexchange():
    return load_exchange(c.PAPER)

@pytest.fixture(scope="class")
def perf_tracker():
    return PerformanceTracker(
        starting_cash=0.0,
        timeframe=Timeframe.ONE_MIN
    )

@pytest.fixture(scope="class")
def portfolio(perf_tracker):
    return Portfolio(
        starting_cash=0.0,
        perf_tracker=perf_tracker, # option to override, otherwise default
        positions=None # option to override with existing positions
    )

@pytest.fixture(scope="class")
def balance():
    return Balance(
        cash_currency=c.BTC,
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
        cost_price=0.0,
        fee=0.0
    )

@pytest.fixture(scope="class")
def trade(asset):
    return Trade(
        trade_id=None,
        exchange_id=None,
        exchange_order_id=159025,
        asset=asset,
        price=0.0,
        quantity=0.0,
        trade_time=datetime.utcnow(),
        side="buy",
        fee=0.0
    )
