import pandas as pd

def bollinger_state(klines, period=20, dev=2):
    closes = [float(k[4]) for k in klines]
    df = pd.DataFrame({"close": closes})

    ma = df["close"].rolling(period).mean()
    std = df["close"].rolling(period).std()

    upper = ma + dev * std
    lower = ma - dev * std

    width = (upper - lower) / ma

    return {
        "close": df["close"].iloc[-1],
        "ma": ma.iloc[-1],
        "upper": upper.iloc[-1],
        "lower": lower.iloc[-1],
        "width": width.iloc[-1]
    }