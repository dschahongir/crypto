import statistics

def adaptive_bollinger(closes, atr, base_period=20):
    if len(closes) < base_period or atr is None:
        return None

    sma = sum(closes[-base_period:]) / base_period
    std = statistics.stdev(closes[-base_period:])

    multiplier = 2.0 if atr / sma < 0.01 else 2.5

    upper = sma + multiplier * std
    lower = sma - multiplier * std
    close = closes[-1]
    width = (upper - lower) / sma if sma else 0.0

    return {
        "upper": upper,
        "lower": lower,
        "middle": sma,   # оставим для старого кода
        "ma": sma,       # для phase_detector
        "close": close,  # для phase_detector
        "width": width,  # для phase_detector
    }