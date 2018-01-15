import time

from punisher.trading import order_manager
from punisher.trading.context import Context, default_config, TradingMode
from punisher.exchanges.exchange import load_exchange


def backtest(run_name,
             strategy,
             config=default_config(TradingMode.BACKTEST),
             context=None):
    '''
    Backtest entrypoint
    run_name : name of your current experiment (multiple runs per strategy)
    strategy : strategy implementation to be used in this backtest
    config : default or custom config for building a Backtest Context
    context: None by default, but will override the config if it is passed in.
    '''

    if context:
        ctx = context
    else:
        ctx = Context.from_config(config)

    ctx.logger.info("Starting backtest ...")
    ctx.logger.info(ctx.config)

    record = ctx.record
    feed =  ctx.feed
    exchange = ctx.exchange

    while True:
        row = feed.next()
        if row is not None:
            orders = strategy.process(row, ctx)

        # TODO: Implement Cancelling orders
        # should we auto-cancel any outstanding orders
        # order_manager.cancel_orders(orders['cancel_ids'])

        # Returns both FILLED and PENDING orders
        # TODO: Order manager handles mapping from Exchange JSON
        # Paricularly order types like CLOSED --> FILLED,
        # And OPEN vs PENDING <-- check the 'quantity' vs 'filled' amounts
        orders = order_manager.place_orders(exchange, orders)
        filled_orders = order_manager.get_filled_orders(orders)

        # Portfolio only needs to know about new FILLED orders
        record.portfolio.update(filled_orders)

        # Record needs to know about ALL new orders (open/filled)
        for order in orders:
            record.orders[order.id] = order

        # TODO: Update Balance
        # We're not updating the virtual balance, only the exchange
        # which is OK until we have a multi-exchange algo
        # But this also means, for live trading, we can't separate
        # fund from Algo to Algo.
        record.balance = exchange.balance

        # Save to file
        record.save()

    return record


def simulation(run_name,
               strategy,
               config=default_config(TradingMode.SIMULATION),
               context=None):
    '''
    Simulation entrypoint
    run_name : name of your current experiment (multiple runs per strategy)
    strategy : strategy implementation to be used in this simulation
    config : default or custom config for building a Simulation Context
    context: None by default, but will override the config if it is passed in.
    '''

    if context:
        ctx = context
    else:
        ctx = Context.from_config(config)

    ctx.logger.info("Starting Simulation ...")
    ctx.logger.info(ctx.config)

    record = ctx.record
    feed = ctx.feed
    exchange = ctx.exchange

    while True:
        row = feed.next()
        if row is not None:
            orders = strategy.process(row, ctx)

        # TODO: Implement Cancelling orders
        # should we auto-cancel any outstanding orders
        # or should we leave this decision up to the Strategy?
        # order_manager.cancel_orders(orders['cancel_ids'])

        # Returns both FILLED and PENDING orders
        # TODO: Order manager handles mapping from Exchange JSON
        # Paricularly order types like CLOSED --> FILLED,
        # And OPEN vs PENDING <-- check the 'quantity' vs 'filled' amounts
        orders = order_manager.place_orders(ctx.exchange, orders)

        # Record needs to know about ALL new orders (open/filled)
        for order in orders:
            ctx.record.orders[order.id] = order

        # Portfolio only needs to know about new FILLED orders
        filled_orders = order_manager.get_filled_orders(orders)
        record.portfolio.update(filled_orders)

        # TODO: Update Balance
        # We're not updating the virtual balance, only the exchange
        # which is OK until we have a multi-exchange algo
        # But this also means, for live trading, we can't separate
        # fund from Algo to Algo.
        record.balance = ctx.exchange.balance

        # Save to file
        record.save()

        time.sleep(2)

    return record


def live(run_name, strategy, config, context=None):
    '''
    Live Trading entrypoint.
    run_name : name of your current experiment (multiple runs per strategy)
    strategy : strategy implementation to be used
    config : default or custom config for building a Context
    context: None by default, but will override the config if it is passed in.
    '''

    if context:
        ctx = context
    else:
        ctx = Context.from_config(config)

    record = ctx.record
    feed = ctx.feed
    exchange = ctx.exchange

    ctx.logger.info("Starting Live trading ... CAREFUL!")
    ctx.logger.info(ctx.config)

    while True:
        row = feed.next()
        if row is not None:
            orders = strategy.process(row, ctx)

        # TODO: Implement Cancelling orders
        # should we auto-cancel any outstanding orders
        # or should we leave this decision up to the Strategy?
        # order_manager.cancel_orders(orders['cancel_ids'])

        # Returns both FILLED and PENDING orders
        # TODO: Order manager handles mapping from Exchange JSON
        # Paricularly order types like CLOSED --> FILLED,
        # And OPEN vs PENDING <-- check the 'quantity' vs 'filled' amounts
        orders = order_manager.place_orders(ctx.exchange, orders)

        # Record needs to know about ALL new orders (open/filled)
        for order in orders:
            ctx.record.orders[order.id] = order

        # Portfolio only needs to know about new FILLED orders
        filled_orders = order_manager.get_filled_orders(orders)
        record.portfolio.update(filled_orders)

        # TODO: Update Balance
        # We're not updating the virtual balance, only the exchange
        # which is OK until we have a multi-exchange algo
        # But this also means, for live trading, we can't separate
        # fund from Algo to Algo.
        record.balance = ctx.exchange.balance

        # Save to file
        record.save()

        time.sleep(2)

    return record
