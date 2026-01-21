def atr_filter(atr, price, min_ratio=0.0015):
    if atr is None:
        return False

    return atr / price >= min_ratio