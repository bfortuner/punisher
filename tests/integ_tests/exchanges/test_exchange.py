
def test_fetch_paper_balance(paperexchange):
    print("hi")
    assert paperexchange is not None
    assert paperexchange.fetch_balance().get('BTC') is not None

def test_fetch_live_balance(ccxtexchange):
    assert ccxtexchange is not None
    assert ccxtexchange.fetch_balance().get('BTC') is not None
