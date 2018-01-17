import pytest

def test_fetch_live_balance(ccxtexchange):
    print(ccxtexchange.fetch_balance())
    assert 1
