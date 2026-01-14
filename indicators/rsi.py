import pandas as pd
from ta.momentum import RSIIndicator

def rsi_signal(klines, period=14):
    closes = [float(k[4]) for k in klines]
    df = pd.DataFrame({"close": closes})
    rsi = RSIIndicator(df["close"], window=period).rsi().iloc[-1]

    if rsi < 30:
        return ("RSI_OVERSOLD", round(rsi, 2))
    if rsi > 70:
        return ("RSI_OVERBOUGHT", round(rsi, 2))
    return None