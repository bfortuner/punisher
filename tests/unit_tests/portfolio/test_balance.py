import math
from copy import deepcopy

from punisher.portfolio.balance import BalanceType
from punisher.trading import coins
from punisher.trading.order_manager import (build_limit_buy_order,
                                            build_limit_sell_order)
from punisher.trading.order import OrderStatus

class TestSingleExchange:
    def test_balance(self, balance):

        assert balance is not None
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 0.0
        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 0.0

    def test_update_with_created_order_buy(
            self, balance, paperexchange, asset):
        balance = deepcopy(balance)
        balance.update(coins.BTC, 10, 0.0)
        balance.update(coins.USDT, 10, 0.0)
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 10.0
        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 10.0

        quantity = 1.0
        price = 1.0
        start_time = paperexchange.data_provider.get_time()
        order = build_limit_buy_order(
            balance, paperexchange, asset, quantity, price, start_time)

        balance.update_with_created_order(order)
        # No change to BTC on created buy order
        assert balance.get(coins.BTC)[BalanceType.FREE] == 10.0
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 10.0
        assert balance.get(coins.BTC)[BalanceType.USED] == 0.0

        # 1 USDT FREE balance should move into USED
        assert balance.get(coins.USDT)[BalanceType.FREE] == 9.0
        assert balance.get(coins.USDT)[BalanceType.USED] == 1.0
        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 10.0


    def test_update_with_created_order_sell(
            self, balance, paperexchange, asset):
        # resetting the balance
        balance = deepcopy(balance)
        balance.update(coins.BTC, 10, 0.0)
        balance.update(coins.USDT, 10, 0.0)
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 10.0
        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 10.0

        quantity = 1.0
        price = 1.0
        start_time = paperexchange.data_provider.get_time()
        order = build_limit_sell_order(
            balance, paperexchange, asset, quantity, price, start_time)

        balance.update_with_created_order(order)
        # BTC funds move from FREE to USED
        assert balance.get(coins.BTC)[BalanceType.FREE] == 9.0
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 10.0
        assert balance.get(coins.BTC)[BalanceType.USED] == 1.0

        # No Changed to USDT yet on sell
        assert balance.get(coins.USDT)[BalanceType.FREE] == 10.0
        assert balance.get(coins.USDT)[BalanceType.USED] == 0.0
        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 10.0


    def test_update_with_failed_order_buy(
            self, balance, paperexchange, asset):
        # resetting the balance
        balance = deepcopy(balance)
        balance.update(coins.BTC, 10, 0.0)
        # Setting quote funds to a Created order state
        balance.update(coins.USDT, 9, 1)
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 10.0
        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 10.0

        quantity = 1.0
        price = 1.0
        start_time = paperexchange.data_provider.get_time()
        order = build_limit_buy_order(
            balance, paperexchange, asset, quantity, price, start_time)

        # Updating the order status to failed
        order.status = OrderStatus.FAILED
        balance.update_with_failed_order(order)

        # No change to BTC on a 0 trade failed order
        assert balance.get(coins.BTC)[BalanceType.FREE] == 10.0
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 10.0
        assert balance.get(coins.BTC)[BalanceType.USED] == 0.0

        # Quote funds move back to Free from used
        assert balance.get(coins.USDT)[BalanceType.FREE] == 10.0
        assert balance.get(coins.USDT)[BalanceType.USED] == 0.0
        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 10.0


    def test_update_with_failed_order_sell(
            self, balance, paperexchange, asset):
        # resetting the balance
        balance = deepcopy(balance)
        balance.update(coins.BTC, 9, 1)
        # Setting quote funds to a Created order state
        balance.update(coins.USDT, 10, 0.0)
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 10.0
        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 10.0

        quantity = 1.0
        price = 1.0
        start_time = paperexchange.data_provider.get_time()
        order = build_limit_sell_order(
            balance, paperexchange, asset, quantity, price, start_time)

        # Updating the order status to failed
        order.status = OrderStatus.FAILED
        balance.update_with_failed_order(order)

        # BTC funds for sale move back to FREE on failed
        # 0 trade sell order
        assert balance.get(coins.BTC)[BalanceType.FREE] == 10.0
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 10.0
        assert balance.get(coins.BTC)[BalanceType.USED] == 0.0

        # No change to USDT funds on failed 0 trade sell order
        assert balance.get(coins.USDT)[BalanceType.FREE] == 10.0
        assert balance.get(coins.USDT)[BalanceType.USED] == 0.0
        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 10.0

    # TODO: Test updating on trades
    # TODO: Test partial filled Failed order updates
