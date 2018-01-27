import math
import pytest
from datetime import datetime
from copy import deepcopy
from punisher.trading import coins
from punisher.trading.order import OrderStatus

from punisher.trading.order_manager import (build_limit_buy_order,
                                            build_limit_sell_order,
                                            get_created_orders,
                                            get_open_orders,
                                            get_filled_orders,
                                            get_canceled_orders,
                                            get_failed_orders,
                                            process_orders)
class TestProcessOrders:

    def test_setup(self, paperexchange, balance, portfolio):
        balance.update(coins.USD, 20000, 0.0)
        paperexchange.balance = deepcopy(balance)

    def test_order_manager(self, paperexchange, asset, balance):
        quantity = 1.0
        price = 10000.0
        buy_order = build_limit_buy_order(
                    paperexchange, asset, quantity, price, datetime.utcnow())

        updated_orders = process_orders(
                        paperexchange, balance, [buy_order])

        print("updated orders: ", updated_orders)

    def test_insufficient_balance(self, paperexchange, asset, balance):
        quantity = 1.0
        price = 11000.0
        buy_order = build_limit_buy_order(
                    paperexchange, asset, quantity, price, datetime.utcnow())

        updated_orders = process_orders(
                        paperexchange, balance, [buy_order])



        # print("updated orders: ", updated_orders)
        # print("exchange balance: ", paperexchange.balance)
        # print("local balance: ", balance)


class TestGetOrdersByTypes:

    def test_get_created_order(self, paperexchange, asset):
        quantity = 1.0
        price = 10000.0
        order = build_limit_buy_order(
            paperexchange, asset, quantity, price, datetime.utcnow())

        assert get_created_orders([order]) == [order]

    def test_get_open_order(self, paperexchange, asset):
        quantity = 1.0
        price = 10000.0
        order = build_limit_buy_order(
            paperexchange, asset, quantity, price, datetime.utcnow())

        order.status = OrderStatus.OPEN
        assert get_open_orders([order]) == [order]

    def test_get_filled_order(self, paperexchange, asset):
        quantity = 1.0
        price = 10000.0
        order = build_limit_buy_order(
            paperexchange, asset, quantity, price, datetime.utcnow())
        order.status = OrderStatus.FILLED

        assert get_filled_orders([order]) == [order]

    def test_get_canceled_order(self, paperexchange, asset):
        quantity = 1.0
        price = 10000.0
        order = build_limit_buy_order(
            paperexchange, asset, quantity, price, datetime.utcnow())
        order.status = OrderStatus.CANCELED

        assert get_canceled_orders([order]) == [order]

    def test_get_failed_order(self, paperexchange, asset):
        quantity = 1.0
        price = 10000.0
        order = build_limit_buy_order(
            paperexchange, asset, quantity, price, datetime.utcnow())
        order.status = OrderStatus.FAILED

        assert get_failed_orders([order]) == [order]
