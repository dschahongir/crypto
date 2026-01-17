from binance.client import Client
from config.settings import BINANCE_API_KEY, BINANCE_API_SECRET

# Инициализация клиента (для REST API)
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

def fetch_initial_history(symbol, interval="1m", limit=100):
    """
    Скачивает исторические свечи при старте бота, 
    чтобы не ждать 50 минут заполнения буфера.
    """
    try:
        raw_klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        clean_klines = []

        for k in raw_klines:
            clean_klines.append({
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
                "close_time": k[6]
            })
        
        print(f"✅ {symbol}: Загружено {len(clean_klines)} исторических свечей")
        return clean_klines
        
    except Exception as e:
        print(f"❌ Ошибка загрузки истории для {symbol}: {e}")
        return []