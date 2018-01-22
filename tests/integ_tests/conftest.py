import pytest

from punisher import constants as c
from punisher.exchanges import ex_cfg
from punisher.exchanges import load_exchange


@pytest.fixture(scope="module")
def ccxtexchange():
    return load_exchange(ex_cfg.BINANCE)

@pytest.fixture(scope="module")
def paperexchange():
    return load_exchange(ex_cfg.PAPER)
