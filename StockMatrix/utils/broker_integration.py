import ccxt

def fetch_live_price(exchange_name, symbol):
    exchange_class = getattr(ccxt, exchange_name)()
    ticker = exchange_class.fetch_ticker(symbol)
    return ticker['last']

def place_order(exchange_name, symbol, side, amount, price=None):
    exchange_class = getattr(ccxt, exchange_name)({'apiKey':'YOUR_KEY','secret':'YOUR_SECRET'})
    if price:
        return exchange_class.create_limit_order(symbol, side, amount, price)
    else:
        return exchange_class.create_market_order(symbol, side, amount)
