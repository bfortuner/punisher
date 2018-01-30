import math
import pytest
from copy import deepcopy
from punisher.trading import coins
from punisher.trading.order import OrderStatus
from punisher.portfolio.balance import BalanceType
import punisher.trading.order_manager as om


class TestProcessOrders:

    def test_setup(self, paperexchange, balance, portfolio):
        balance.update(coins.USDT, 20000, 0.0)
        paperexchange.balance = deepcopy(balance)

        assert balance is not paperexchange.balance
        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 20000
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 0.0

    def test_order_manager(self, paperexchange, asset, balance):
        quantity = 1.0
        price = 10000.0
        start_time = paperexchange.data_provider.get_time()
        buy_order = om.build_limit_buy_order(
            balance, paperexchange, asset, quantity, price, start_time)

        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 20000
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 0.0
        updated_orders = om.process_orders(
            paperexchange, balance, [buy_order])

        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 20000
        assert balance.get(coins.USDT)[BalanceType.FREE] == 10000
        assert balance.get(coins.USDT)[BalanceType.USED] == 10000
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 0.0

        print("updated orders: ", updated_orders)

    def test_insufficient_balance(self, paperexchange, asset, balance):
        quantity = 1.0
        price = 11000.0
        start_time = paperexchange.data_provider.get_time()
        buy_order = om.build_limit_buy_order(
            balance, paperexchange, asset, quantity, price, start_time)

        assert buy_order.status == OrderStatus.FAILED


class TestGetOrdersByTypes:

    def test_setup(self, paperexchange, balance):
        balance.update(coins.USDT, 20000, 0.0)
        paperexchange.balance = deepcopy(balance)

        assert balance is not paperexchange.balance
        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 20000
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 0.0

    def test_get_created_order(self, paperexchange, asset, balance):
        quantity = 1.0
        price = 10000.0
        start_time = paperexchange.data_provider.get_time()
        order = om.build_limit_buy_order(
            balance, paperexchange, asset, quantity, price, start_time)

        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 20000
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 0.0
        assert om.get_created_orders([order]) == [order]

    def test_get_open_order(self, paperexchange, asset, balance):
        quantity = 1.0
        price = 10000.0
        start_time = paperexchange.data_provider.get_time()
        order = om.build_limit_buy_order(
            balance, paperexchange, asset, quantity, price, start_time)

        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 20000
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 0.0
        order.status = OrderStatus.OPEN
        assert om.get_open_orders([order]) == [order]

    def test_get_filled_order(self, paperexchange, asset, balance):
        quantity = 1.0
        price = 10000.0
        start_time = paperexchange.data_provider.get_time()
        order = om.build_limit_buy_order(
            balance, paperexchange, asset, quantity, price, start_time)
        order.status = OrderStatus.FILLED

        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 20000
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 0.0
        assert om.get_filled_orders([order]) == [order]

    def test_get_canceled_order(self, paperexchange, asset, balance):
        quantity = 1.0
        price = 10000.0
        start_time = paperexchange.data_provider.get_time()
        order = om.build_limit_buy_order(
            balance, paperexchange, asset, quantity, price, start_time)
        order.status = OrderStatus.CANCELED

        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 20000
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 0.0
        assert om.get_canceled_orders([order]) == [order]

    def test_get_failed_order(self, paperexchange, asset, balance):
        quantity = 1.0
        price = 10000.0
        start_time = paperexchange.data_provider.get_time()
        order = om.build_limit_buy_order(
            balance, paperexchange, asset, quantity, price, start_time)
        order.status = OrderStatus.FAILED

        assert balance.get(coins.USDT)[BalanceType.TOTAL] == 20000
        assert balance.get(coins.BTC)[BalanceType.TOTAL] == 0.0
        assert om.get_failed_orders([order]) == [order]


    # TODO:
    # get the filled order among other non-filled
    # get multiple filled orders
    # No filled orders
