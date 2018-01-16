# TODO

### Research

* Explore papers / projects using twitter for sentiment, news analysis on stocks/crypto
* Explore machine learning research / projects for price prediction, portfolio optimization, and news/event

### Data / Feeds

* Implement load multiple assets ( using same schema as other feeds )
* Add ability for a live feed to initialize with historical data, but have the model start at present time
* How to handle a missed data point? When the feed is delayed? When timesteps are missing?

### Record

* How to store multiple runs of the same strategy with different hyperparameters? Right now we will override previous values.

### Strategies

* Create example strategy files
  * Momentum (SMA)
  * Random Buy/Sell
  * Portfolio optimization
  * Exchange Arbitrage

### Ordering

* Add method rebalancePortfolio(assets, weights) to OrderManager which places the necessary buy/sell orders to rebalance a portfolio provided a list of weights
* How to handle pending orders? Always cancel? Edit? Reorder?

### Trading

* Add ability to trade multiple assets in same strategy
* How to handle pending orders? Always cancel? Edit? Reorder? Implement and test with paper and live trading.
* Create commission functionality for paper exchange
* Create slippage model for paper exchange
* Add Margin Ordering + Accounts
* Add method to fetch exchange rates and quote balance in any currency

### Dash Visualizations

* Unify timeframe across charts in Dash - Separate charts don't always align time-wise (when historical ohlcv starts before ordering)
* Plot Cash levels line chart
* Plot portfolio allocation bar chart (position weights)
* Plot balance by coin bar chart
* Plot chart of Buy/Sell orders per time period
* Plot "benchmark" PnL/Returns (provided by user)

### Indicators / Metrics

* SMA (Simple Moving Average method)

### Refactoring

* Finalize user experience for running experiments
* Break up constants.py into smaller files within submodules (i.e. keep values near where they're used)
* Possibly switch to relative imports
* Map our OrderStatus, type, and side to CCXT equivalents

### Testing

* Test full trading lifecycle (backtest, sim, live)
* Test Limit orders
* Test Canceling orders

### Known Issues / Bugs

* Fix date conversion issues -Epoch to utc (or remove the time_epoch)
* Fetching historical data using 1m period only goes back 1 day and may cause bugs when using start/end
* We don't support multiple assets yet, need to figure out what to load into df(s) for each feed type
