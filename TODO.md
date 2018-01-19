# TODO

### Research

* Explore papers / projects using twitter for sentiment, news analysis on stocks/crypto
* Explore machine learning research / projects for price prediction, portfolio optimization, and news/event

### Balance

* Verify starting_cash <= actual balance on Live Exchange
* Audit method to verify local balance == exchange balance for duration of strategy (assuming no other transactions are taking place)

### Data / Feeds

* Add support for Multiple Assets in OHLCV feed
* Add support for Multiple Exchanges in OHLCV feed
* Add ability for a live feed to initialize with historical data, but have the model start at present time
* How to handle a missed data point? When the feed is delayed? When timesteps are missing?
* Add the Brave New Coin Feed (which aggregates pricing information across exchanges)

### Record

* How to store multiple runs of the same strategy with different hyperparameters? Right now we will override previous experiment run.

### Strategies

* Create example strategy files
  * Buy/Hold
  * Momentum (SMA)
  * Mean Reversion
  * Multiple Assets
  * Portfolio optimization
  * Exchange Arbitrage

### Ordering

* Add method rebalancePortfolio(assets, weights) to OrderManager which places the necessary buy/sell orders to rebalance a portfolio provided a list of weights (Portfolio Optimization)
* How to handle open orders not filled after X amount of time? Always cancel? Edit? Reorder?

### Portfolio

* Track USD value of positions
* Update Position to take an exchange_id
* Refactor Positions and Performance to account for positions across exchanges
* Update Position values with prices from the same exchange

### Trading

* Add method to fetch exchange rates and quote balance in any currency
* Add USD benchmark for all trading strategies
* Add fees into position value calculations for live trading (we store them but don't use them)
* Create fees model for paper exchange
* Add ability to trade multiple assets in same strategy
* Create slippage model for paper exchange
* Add Margin Ordering + Accounts

### Dash Visualizations

* Launch Dash inside the Strategy Script (separate thread)
* Unify timeframe across charts in Dash - Separate charts don't always align time-wise (when historical ohlcv starts before ordering)
* Plot Cash levels line chart
* Plot USD value of Cash/Positions
* Plot portfolio allocation bar chart (position weights)
* Dropdown Asset OHLCV pricing chart (multiple assets)
* Dropdown Exchange OHLCV pricing chart (multiple exchange price data in feed)
* Plot balance by coin bar chart
* Plot chart of Buy/Sell orders per time period
* Plot "benchmark" PnL/Returns (provided by user)
* Create a multi-page Dash app where we can view multiple strategies running (stop/start/pause them)

### Indicators / Metrics

* SMA (Simple Moving Average method)

### Refactoring

* Break up constants.py into smaller files within submodules (i.e. keep values near where they're used)
* Possibly switch to relative imports

### Testing

* Start writing Unit tests anytime a class or function is updated
* Test full trading lifecycle (backtest, sim, live)
* Test Canceling orders

### Known Issues / Bugs

* Feed waits 1 full period before trigging an action in the Strategy. This is annoying.
* Fix date conversion issues -Epoch to utc (or remove the time_epoch)
* Fetching historical data using 1m period only goes back 1 day and may cause bugs when using start/end
* We don't support multiple assets yet, need to figure out what to load into df(s) for each feed type
