import os 

# === НАСТРОЙКИ BINANCE ===
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "ТВОЙ_КЛЮЧ")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "ТВОЙ_СЕКРЕТ")

# === НАСТРОЙКИ TELEGRAM ===
TELEGRAM_API_TOKEN = "ТВОЙ_ТОКЕН"
TELEGRAM_CHAT_ID = "ТВОЙ_ID"

# === ПОВЕДЕНИЕ БОТА ===
USE_WATCHLIST_ONLY = True

# 🔥 Оптимизированный список (ТОП активных монет)
# Убрали дубликаты и "мертвые" монеты.
WATCHLIST = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", 
    "ADAUSDT", "AVAXUSDT", "DOGEUSDT", "DOTUSDT", "MATICUSDT",
    "LTCUSDT", "LINKUSDT", "ATOMUSDT", "NEARUSDT", "APTUSDT",
    "ARBUSDT", "OPUSDT", "INJUSDT", "RUNEUSDT", "FTMUSDT"
]

SCAN_INTERVAL_SEC = 600
SIGNAL_COOLDOWN_MIN = 30