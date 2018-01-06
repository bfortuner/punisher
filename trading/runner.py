import time
from enum import Enum, unique


@unique
class TradeMode(Enum):
    BACKTEST = 0
    SIMULATE = 1
    LIVE = 2


class Punisher():
    def __init__(self, exchange, feed, strategy, record):
        self.exchange = exchange
        self.feed = feed
        self.strategy = strategy
        self.record = record
        
    def backtest(self):
        results = []
        row = self.feed.next()
        while row is not None:
            print("Timestep", row['time_utc'], "Price", row['close'])
            row = self.feed.next()
            output = self.strategy(row, self.exchange, self.feed)
            results.append(output)
        return results
    
    def simulate(self):
        while True:
            row = self.feed.next()
            if row is not None:
                output = self.strategy(row, self.exchange, self.feed)
                self.record['test'].append(output)
            time.sleep(2)

    def live(self):
        while True:
            row = self.feed.next()
            if row is not None:
                output = self.strategy(row, self.exchange, self.feed)
                self.record['live'].append(output)
            time.sleep(2)
    
    def punish(self, mode=False):
        if mode == TradeMode.BACKTEST:
            print("Backtesting ...")
            self.backtest()
        elif mode == TradeMode.SIMULATE:
            print("Simulating orders ...")
            self.simulate()
        elif mode == TradeMode.LIVE:
            print("LIVE TRADING! CAREFUL!")
            self.live()