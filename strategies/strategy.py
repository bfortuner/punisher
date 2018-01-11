import datetime


class Strategy():
    def __init__(self, logger=None):
        self.name = self.__class__.__name__
        self.epoch = 1
        self.logger = logger

    def log(self, msg):
        if self.logger is not None:
            self.logger.info(msg)

    def log_epoch_time(self, time_utc):
        self.log("---------------------------------------")
        self.log("Epoch {:d} - Timestep: {:s}".format(
            self.epoch, time_utc.isoformat()
        ))
        self.log("---------------------------------------")

    def log_ohlcv(self, data):
        self.log("OHLCV")
        self.log("    O: {:.4f} | C: {:.4f} | V: {:.1f} | T: {:s}".format(
            data['open'], data['close'], data['volume'],
            data['time_utc'].isoformat()))

    def log_performance(self, cxt):
        self.log("PERFORMANCE")
        port = cxt.record.portfolio
        self.log("    Cash: {:.4f} Total Val: {:.4f} PnL: {:.4f} Returns: {:.4f}".format(
            port.cash, port.total_value, port.perf.pnl, port.perf.returns))

    def log_metrics(self, ctx):
        self.log("METRICS")
        metrics = ctx.record.metrics
        for m in metrics.keys():
            self.log("    {:s}: {:.2f}".format(m, metrics[m][-1]))

    def log_balance(self, ctx):
        self.log("BALANCE")
        b = ctx.record.balance
        for c in b.currencies:
            self.log("    {:s} - {:s}".format(c, str(b.to_dict()[c]), indent=2))

    def log_positions(self, ctx):
        self.log("POSITIONS")
        for p in ctx.record.portfolio.positions:
            self.log("     {:s}".format(str(p.to_dict())))

    def log_orders(self, orders):
        self.log("ORDERS")
        for i,order in enumerate(orders):
            if order.price is None:
                order.price = 0.0
            self.log("    {:d}: {:s} | {:s} | Price: {:.4f} | Quantity: {:.4f}".format(
                i+1,order.asset.symbol, order.order_type.name,
                order.price, order.quantity))

    def process(self, data, ctx):
        output = self.handle_data(data, ctx)
        self.epoch += 1
        return output

    def update_metric(self, name, val, ctx):
        metrics = ctx.record.metrics
        if name not in metrics.keys():
            metrics[name] = [val]
        else:
            metrics[name].append(val)

    def update_ohlcv(self, data, ctx):
        ctx.record.add_ohlcv(data)

    def handle_data(self, data, ctx):
        orders = []
        return orders
