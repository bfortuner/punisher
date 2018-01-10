import datetime

class Strategy():
    def __init__(self):
        self.epoch = 1

    def log(self, msg, dt=None):
        dt = dt or datetime.datetime.utcnow()
        print('%s, %s' % (dt.isoformat(), msg))

    def process(self, data, context):
        self.log("Epoch {:d}".format(self.epoch))
        output = self.handle_data(data, context)
        self.epoch += 1
        return output

    def update_metric(self, name, val, context):
        metrics = context.record.metrics
        if name not in metrics.keys():
            metrics[name] = [val]
        else:
            metrics[name].append(val)

    def handle_data(self, data, context):
        orders = []
        return orders


class SimpleStrategy(Strategy):
    def __init__(self):
        super().__init__()

    def handle_data(self, data, context):
        self.log(data)
        context.record.add_ohlcv(data)

        # Update metrics
        self.update_metric('SMA', 5.0, context)
        self.update_metric('RSI', 10.0, context)

        orders = []
        return orders
