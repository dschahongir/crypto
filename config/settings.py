import os 

# === НАСТРОЙКИ BINANCE ===
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "Duq52TQKYdrKgZ4qMpHsu5YcPdPbw0Cxreit8G1KpuPVaUFcWI0nwgWjDOZh74ZH")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "m1iIffyrCbuznHQQN6KxFkPkG7Fyl5YtZ43XV5DlJAz2okZhhN6Zjksqa03yuEuef")

# === НАСТРОЙКИ TELEGRAM ===
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN", "8301469967:AAE9rub_3iZ9GX8T18mE63fvGY-LFdBWtec")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1820081448")

# === ПОВЕДЕНИЕ БОТА ===
USE_WATCHLIST_ONLY = True

# 🔥 Оптимизированный список (ТОП активных монет)
# Убрали дубликаты и "мертвые" монеты.
WATCHLIST = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "AVAXUSDT", 
    "DOGEUSDT", "TRXUSDT", "DOTUSDT", "MATICUSDT", "LTCUSDT", "SHIBUSDT", "LINKUSDT", 
    "BCHUSDT", "ATOMUSDT", "XLMUSDT", "UNIUSDT", "NEARUSDT", "APTUSDT", "FILUSDT", 
    "HBARUSDT", "LDOUSDT", "ICPUSDT", "VETUSDT", "ARBUSDT", "OPUSDT", "RNDRUSDT", 
    "QNTUSDT", "GRTUSDT", "MKRUSDT", "SNXUSDT", "STXUSDT", "AAVEUSDT", "ALGOUSDT", 
    "AXSUSDT", "SANDUSDT", "EOSUSDT", "IMXUSDT", "THETAUSDT", "XTZUSDT", "EGLDUSDT", 
    "FTMUSDT", "INJUSDT", "RUNEUSDT", "FLOWUSDT", "KAVAUSDT", "GALAUSDT", "CHZUSDT", 
    "PEPEUSDT", "SUIUSDT", "SEIUSDT", "TIAUSDT", "ORDIUSDT", "1000SATSUSDT"
]

SCAN_INTERVAL_SEC = 600
SIGNAL_COOLDOWN_MIN = 30