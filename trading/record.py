from datetime import datetime
from trading.orders import Order
from trading.orders import OrderType, OrderStatus

import utils.files


class RecordConfig():
    """
    Not required (could replace w Dictionary), but a 
    good place to show what values we need in the dict
    """
    def __init__(self, dict_):
        self.values = {
            'root': dict_['root'], # path to csv files
            'strategy': dict_['strategy'], # name of strategy 
            'assets': dict_['assets'], # optional
            'exchanges': dict_['exchanges'],
            'cash_asset': dict_['cash_asset'],
            'cash_balance': dict_['cash_balance'],
        }


class Record():
    def __init__(self, config):        
        # Keys - Directory, Strategy, Time, Symbol, FPath
        self.cfg = config.values
        self.orders = {} # dataframe?
        self.balance = {}
        self.data = [] # price, ohlcv, twitter, events (pulled from at each timestep)
        self.metrics = [
            # {'name': Metric.SMA50, 'values': [2.3, 1.23, 12.4 ...] },
            # {'name': Metric.RSI, 'values': [2.3, 1.23, 12.4 ...] }
        ]


    ## BALANCE

    def get_balance(self):
        return self.balance

    def set_balance(self, balance):
        """
        Is Balance an Object or Dictionary?
        Do we include methods here to update
        the items in the balance or do we let
        external functions do that?
        """
        self.balance = balance


    ## POSITIONS

    def get_positions(self):
        """
        Recreate from Order History?
        External function for sure
        """
        pass


    ## ORDERS

    def get_orders(self):
        return self.orders

    def set_orders(self, orders):
        self.orders = orders

    def get_pending_orders(self):
        pending_orders = []
        for _, order in self.orders.items():
            if order.get_status() in [OrderStatus.NEW, OrderStatus.ATTEMPED]:
                pending_orders.append(order)
        return pending_orders
    
    def get_order_by_id(self, order_id):
        return self.orders['order_id']

    def get_order_by_exchange_id(self, ex_order_id):
        for _, order in self.orders.items():
            if order.exchange_order_id == ex_order_id:
                return order
        return None


    ## STATE
    def save_record(self):
        self.save_orders()
        self.save_decisions()
        self.save_data()

    def save_orders(self):
        fpath = os.path.join(self.cfg['root'], c.ORDER_FNAME)
        utils.files.save_dict_to_csv(fpath, self.orders)

    def save_decisions(self):
        fpath = os.path.join(self.cfg['root'], c.DECISIONS_FNAME)
        utils.files.save_dict_to_csv(fpath, self.orders)

    def save_data(self):
        fpath = os.path.join(self.cfg['root'], c.RECORD_DATA_FNAME)
        utils.files.save_dict_to_csv(fpath, self.orders)

    def save_config(self):
        fpath = os.path.join(self.cfg['root'], c.CONFIG_FNAME)
        utils.files.save_json(fpath, self.cfg)

    def load_record(self):
        return None

