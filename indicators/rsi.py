import pandas as pd
from ta.momentum import RSIIndicator

def rsi_signal(closes, period=14):
    """Возвращает чистое значение RSI."""
    if len(closes) < period + 1:
        return 50.0 # Нейтральное значение, если данных мало

    # Преобразуем в Series для библиотеки ta
    series = pd.Series([float(c) for c in closes])
    
    try:
        rsi = RSIIndicator(series, window=period).rsi().iloc[-1]
        return round(rsi, 2)
    except:
        return 50.0