import datetime

class Strategy():
    def __init__(self, context):
        self.ctx = context
        self.epoch = 1

    def log(self, msg, dt=None):
        dt = dt or datetime.datetime.utcnow()
        print('%s, %s' % (dt.isoformat(), msg))

    def process(self, data):
        self.log("Epoch {:d}".format(self.epoch))
        output = self.handle_data(data)
        self.epoch += 1
        return output

    def update_metric(self, name, val):
        metrics = self.ctx.record.metrics
        if name not in metrics.keys():
            metrics[name] = [val]
        else:
            metrics[name].append(val)

    def handle_data(self, data):
        orders = []
        return orders


class SimpleStrategy(Strategy):
    def __init__(self, context):
        super().__init__(context)

    def handle_data(self, data):
        print ("PUNISHED!")

        # Update metrics
        self.update_metric('SMA', 5.0)
        self.update_metric('RSI', 10.0)

        orders = []
        return orders
