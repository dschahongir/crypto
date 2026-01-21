import pandas as pd
from ta.momentum import RSIIndicator

def rsi_signal(closes, period=14):
    """Возвращает сигнал RSI по списку закрытий."""
    if len(closes) < period + 1:
        return None

    closes = [float(price) for price in closes]
    df = pd.DataFrame({"close": closes})
    rsi = RSIIndicator(df["close"], window=period).rsi().iloc[-1]

    if rsi < 30:
        return ("RSI_OVERSOLD", round(rsi, 2))
    if rsi > 70:
        return ("RSI_OVERBOUGHT", round(rsi, 2))
    return None