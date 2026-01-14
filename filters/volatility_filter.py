def atr_filter(atr, price, min_ratio=0.003):
    """
    min_ratio = 0.3% от цены
    """
    if atr is None:
        return False

    return atr / price >= min_ratio