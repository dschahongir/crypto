import statistics

def adaptive_bollinger(closes, atr, base_period=20):
    if len(closes) < base_period or atr is None:
        return None

    sma = sum(closes[-base_period:]) / base_period
    std = statistics.stdev(closes[-base_period:])

    # 📌 адаптация ширины под волатильность
    multiplier = 2.0 if atr / sma < 0.01 else 2.5

    upper = sma + multiplier * std
    lower = sma - multiplier * std

    return {
        "upper": upper,
        "lower": lower,
        "middle": sma
    }