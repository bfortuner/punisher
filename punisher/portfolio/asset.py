from punisher.trading import coins


class Asset():
    """
    Base = currency you want to trade
    Quote = currency you want the Base price displayed in

    If you place a BUY order for Base/Quote, it means you're
    buying Base and paying in Quote.

    Other future properties might include:
        * precision
        * supported_exchanges
    """

    def __init__(self, base, quote):
        self.base = base #self.validate_base(base)
        self.quote = quote #self.validate_quote(quote)

    def validate_base(self, base):
        if base not in coins.COINS:
            raise coins.CoinNotSupportedException(base)
        return base

    def validate_quote(self, quote):
        if quote not in coins.CASH_COINS:
            raise coins.CashNotSupportedException(quote)
        return quote

    @property
    def id(self):
        return coins.get_id(self.base, self.quote)

    @property
    def symbol(self):
        return coins.get_symbol(self.base, self.quote)

    @property
    def product(self):
        return coins.get_product(self.base, self.quote)

    def reverse_symbol(self):
        return self.quote + '/' + self.base

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'base': self.base,
            'quote': self.quote,
        }

    @classmethod
    def from_symbol(self, symbol):
        if '/' in symbol:
            base,quote = symbol.split('/')
        elif '_' in symbol:
            base,quote = symbol.split('_')
        else:
            base = symbol[:3]
            quote = symbol[3:]
        return Asset(base, quote)

    def __eq__(self, obj):
        return obj.symbol == self.symbol
