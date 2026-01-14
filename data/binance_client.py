from binance.client import Client
from config.settings import BINANCE_API_KEY, BINANCE_API_SECRET

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

def get_price(symbol):
    return float(client.get_symbol_ticker(symbol=symbol)["price"])

def get_klines(symbol, interval, limit=50):
    return client.get_klines(symbol=symbol, interval=interval, limit=limit)

def get_usdt_pairs():
    info = client.get_exchange_info()
    return [
        s["symbol"]
        for s in info["symbols"]
        if s["quoteAsset"] == "USDT" and s["status"] == "TRADING"
    ]