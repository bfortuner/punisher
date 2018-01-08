import time
from enum import Enum, unique




def run_from_config(config_fpath):
    cfg = load_config()
    exchange = make_exchange(cfg.exchange)
    strategy = load_strategy(cfg.strategy)
    feed = load_feed(cfg.feed)
    record = make_record(cfg.record)
    context = Context(
        exchange=exchange,
        strategy=strategy,
        feed=feed,
        record=record,
        trade_mode=cfg.trade_mode
    )
    punisher.run(context)

def run(context):
    if context.trade_mode == 'backtest':
        return backtest(context)
    elif context.trade_mode == 'simulate':
        return simulate(context)
    elif context.trade_mode == 'live':
        return live(context)


def backtest(context):
    print("Backtesting ...")
    record = Record(record_cfg)
    row = feed.next()
    while row is not None:
        print("Timestep", row['time_utc'], "Price", row['close'])
        row = feed.next()
        if row is not None:
            context = strategy(row, context)
        executor.execute_orders(context)
        time.sleep(1)
        record.save(context)
    return record

def screw_you(exchange, strategy, config, data):
    print("Paper trading ...")
    while True:
        row = self.feed.next()
        if row is not None:
            output = self.strategy(row, self.exchange, self.feed)
            self.record['test'].append(output)
        time.sleep(2)

def live_trade():
    print("LIVE TRADING! CAREFUL!")
    while True:
        row = self.feed.next()
        if row is not None:
            output = self.strategy(row, self.exchange, self.feed)
            self.record['live'].append(output)
        time.sleep(2)
