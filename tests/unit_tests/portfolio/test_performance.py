from datetime import datetime

class TestSingleExchangePerformance:
    def test_performance(self, perf_tracker):
        assert perf_tracker is not None
        # Giving the perf tracker 10000 cash to start
        perf_tracker.starting_cash = 10000
        assert perf_tracker.pnl == 0.0
        assert perf_tracker.returns == 0.0


    def test_add_first_period_long_pos(self, perf_tracker, position):
        position.update(1.0, 10000, 0.0)
        position.latest_price = 10000
        assert position.quantity == 1.0
        assert position.cost_price == 10000
        assert perf_tracker.starting_cash == 10000
        start = datetime.utcnow()

        perf_tracker.add_period(start, 0.0, [position])
        # No change on our positions so should be no profit so far
        assert perf_tracker.pnl == 0.0
        assert perf_tracker.returns == 0.0


    def test_add_second_period_reverse_position(self, perf_tracker, position):
        position.update(-2.0, 11000, 0.0)
        position.latest_price = 11000
        assert position.quantity == -1.0
        assert position.cost_price == 11000
        assert position.cost_value == -11000

        start = datetime.utcnow()
        perf_tracker.add_period(start, 22000, [position])
        assert perf_tracker.pnl == 1000
        assert perf_tracker.returns == 0.1
