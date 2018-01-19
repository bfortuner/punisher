import pytest

from punisher import constants as c
from punisher.exchanges.exchange import load_exchange


@pytest.fixture(scope="module")
def ccxtexchange():
    return load_exchange(c.BINANCE)
