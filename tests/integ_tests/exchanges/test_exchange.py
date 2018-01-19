
def test_fetch_live_balance(ccxtexchange):
    assert ccxtexchange is not None
    assert ccxtexchange.fetch_balance().get('BTC') is not None
