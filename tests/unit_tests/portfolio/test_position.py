import math

class TestSingleExchange:
    def test_position(self, position):

        assert position is not None
        assert position.quantity == 0.0
        assert position.cost_price == 0.0

    def test_new_buy(self, position):
        position.update(1.0, 10000)

        assert position.quantity == 1.0
        assert position.cost_price == 10000

    def test_existing_long_buy(self, position):
        position.update(1.0, 15000)

        assert position.quantity == 2.0
        assert position.cost_price == 12500
        assert position.cost_value == 25000

    def test_new_sell_short(self, position):
        position.update(-2.0, 10000)

        assert position.quantity == 0.0
        assert position.cost_price == 0.0
        assert position.cost_value == 0.0

    def test_short(self, position):
        position.update(-1.0, 10000)

        assert position.quantity == -1.0
        assert position.cost_price == 10000
        assert position.cost_value == -10000

    def test_short_more(self, position):
        position.update(-1.0, 11000)

        assert position.quantity == -2.0
        assert position.cost_price == 10500
        assert position.cost_value == -21000

    def test_cover(self, position):
        position.update(2, 9000)

        assert position.quantity == 0.0
        assert position.cost_price == 0.0
        assert position.cost_value == 0.0

    def test_new_buy2(self, position):
        position.update(1.0, 10000)

        assert position.quantity == 1.0
        assert position.cost_price == 10000


#
# class TestMultiExchange:
#
#     def test_position(self, position):
#         assert position is not None
#         assert position.quantity == 0.0
#         assert position.cost_price == 0.0
#         assert position.exchanges == {}
