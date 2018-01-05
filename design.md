# Punisher Design

## Classes

* DataFeed
* Exchange
* Executor
* Strategy
* Record
* Runner
* Helpers
    * Order
    * OrderStatus
    * OrderType
    * Position
    * OrderType
    * TradeMode
    * Metric <- name

## DataFeed

Data feeds download and refresh information from various sources about pricing, news, events. Feeds are analyzed by the Strategy to make decisions. Feeds can download in bulk or refresh every timestamp (ticker or websocket).

Methods:
* initialize()
* history()
* update()
* next()

Subclasses:
* CSVDataFeed
* ExchangeDataFeed
* TwitterDataFeed
* EventDataFeed

## Exchange

The Exchange class wraps the CCXT client or Dummy client. It pulls information ground truth about orders, balances, fees. It also places trades requested by the executor.

Methods:
* fetch_balance()
* calculate_fee()
* fetch_order()
* create_limit_buy_order()
* create_limit_sell_order()
* cancel_order()

We should keep the method names similar to the CCXT [method names](https://github.com/ccxt/ccxt/blob/master/python/ccxt/base/exchange.py) for consistency.

## Executor

The executor pulls orders from the Record and attempts to place them on the exchange. It updates the Record with order_ids when they succeed and updates their statuses as they change.

* place_orders(Orders[])
* get_outstanding_orders(Record)
* update_orders(Record)
    * Loop through orders in record
    * Retry failed orders
    * Update order statues + ids

## Strategy

The Strategy takes price and news data from the DataFeed and order and balance information from the Record, and returns a Decision about which assets to buy and sell. It can also update/cancel orders. It also considers fees and slippage (from the Exchange).

The strategy defines the logic of our program. It assumes everything will succeed but has access to prior and pending orders along with fees and slippage information from the Exchange. It updates the Record with its Decision, the data it used to make the decision, and the Metrics it calculated.

* Context()
    * DataFeed
        * ohlcv
        * ticker / order book
        * news
    * Record
        * orders
        * positions
        * balance
    * Exchange
        * fees
* Decision()
    * Timestamp
    * orders_to_place = Orders[]
    * orders_to_edit = Orders[]
    * orders_to_cancel = Orders[]

For portfolio optimization it calls helper functions to generate the Orders[] array given an array of percents.

## Order

Orders are stored in the Record and contain the following information. 

* exchange_id
* symbol
* price
* quantity
* OrderType
    * Buy
    * Sell
* OrderStatus
    * Pending
    * Open
    * Filled

## Record

The Record (state) stores information about Decisions, Orders, Positions, and Metrics. It saves data to CSV files at each timestep and returns Pandas Dataframes its callers.

Instance variables
* Orders
* Decisions
* Positions
* Metrics
* Data

Methods
* get_orders()
* get_positions()
* get_balance()
* get_summary()
* update_orders()
* update_positions()
* update_balance()
* load_csv_as_dataframe()
* save_dataframe_as_csv()

## Runner

The Runner (Punisher) provides a consistent interface for all TradeModes (backtest, simulate, live). It loops through data in the feed, passes data to the strategy, sends orders to the Executor, updates the Record, and streams metrics information to services like Kibana, Visdom, or S3.

* Input
    * Strategy
    * Record
    * Executor
    * Exchange
    * Metrics
* punish(TradeMode)
* TradeMode
    * Backtest
    * Simulate
    * Live

It's probably run as a background process.

## Metric

Probably best to leave these as functions called by the Strategy class to make decisions. But we'll want an Enum of metric names to avoid spelling errors in the Record()