import pytest
from punisher import constants as c

@pytest.fixture(scope="module")
def ccxtexchange():
    from punisher.exchanges.exchange import load_exchange
    return load_exchange(c.Binance)
