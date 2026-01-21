def awesome_oscillator(klines):
    """Возвращает значение AO для списка свечей в формате dict."""
    if len(klines) < 34:
        return None

    medians = [(k["high"] + k["low"]) / 2 for k in klines]

    sma5 = sum(medians[-5:]) / 5
    sma34 = sum(medians[-34:]) / 34

    return sma5 - sma34