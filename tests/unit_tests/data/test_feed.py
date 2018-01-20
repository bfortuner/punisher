from pytest_mock import mocker

def inc(x):
    return x + 1

def test_mocker(mocker):
    assert mocker is not None
    assert 1 == 1
