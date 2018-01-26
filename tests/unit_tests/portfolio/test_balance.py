import math
from punisher.portfolio.balance import BalanceType
from punisher.trading import coins

class TestSingleExchange:
    def test_balance(self, balance):

        assert balance is not None
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 0.0
        assert balance.get(coins.USD)[BalanceType.TOTAL] == 0.0
    #
    # def test_new_buy(self, position):
    #     position.update(1.0, 10000)
    #
    #     assert position.quantity == 1.0
    #     assert position.cost_price == 10000
