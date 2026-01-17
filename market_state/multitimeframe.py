import pandas as pd

def calculate_ema(closes, period):
    if len(closes) < period:
        return None
    return pd.Series(closes).ewm(span=period, adjust=False).mean().iloc[-1]

def is_uptrend(closes):
    """
    Тренд вверх, если цена выше EMA 50.
    """
    if len(closes) < 50:
        return False
    
    ema50 = calculate_ema(closes, 50)
    current_price = closes[-1]
    
    return current_price > ema50

def multi_tf_check(data_1m, data_5m, data_15m):
    """
    Проверяем согласованность трендов.
    Чтобы войти в ЛОНГ, старшие таймфреймы не должны смотреть вниз.
    """
    closes_1m = [c["close"] for c in data_1m]
    closes_5m = [c["close"] for c in data_5m]
    closes_15m = [c["close"] for c in data_15m]

    # 1. ГЛАВНЫЙ ФИЛЬТР (15m):
    # Если на 15-минутке мы под EMA50 — глобально тренд вниз, покупать опасно.
    if not is_uptrend(closes_15m):
        return False

    # 2. Локальный фильтр (5m):
    # Также желательно быть выше EMA50
    if not is_uptrend(closes_5m):
        return False

    # 3. Микро-структура (1m):
    # Здесь можно оставить простую проверку: цена не должна валится камнем вниз прямо сейчас
    if closes_1m[-1] < closes_1m[-2] and closes_1m[-2] < closes_1m[-3]:
         return False # Три красные свечи подряд на 1м — ждем остановки падения

    return True