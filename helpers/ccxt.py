import ccxt

SUPPORTED_EXCHANGES = dict(
    binance=ccxt.binance,
    bitfinex=ccxt.bitfinex,
    bittrex=ccxt.bittrex,
    poloniex=ccxt.poloniex,
    bitmex=ccxt.bitmex,
    gdax=ccxt.gdax,
)

def init_exchange(exchange_id, exchange_cfg):
    print('finding {} in CCXT exchanges:\n{}'.format(exchange_id, ccxt.exchanges))
    try:
        # Making instantiation as explicit as possible for code tracking.
        if exchange_name in SUPPORTED_EXCHANGES:
            exchange_attr = SUPPORTED_EXCHANGES[exchange_name]

        else:
            exchange_attr = getattr(ccxt, exchange_name)

        self.api = exchange_attr({
            'apiKey': key,
            'secret': secret,
        })

    except Exception:
        raise ExchangeNotFoundError(exchange_name=exchange_name)