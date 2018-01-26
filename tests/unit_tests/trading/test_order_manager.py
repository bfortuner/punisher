import math
import pytest
from datetime import datetime
from copy import deepcopy
from punisher.trading import coins

from punisher.trading.order_manager import (build_limit_buy_order,
                                            build_limit_sell_order,
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
