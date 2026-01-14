def awesome_oscillator(klines):
    medians = [(float(k[2]) + float(k[3])) / 2 for k in klines]

    if len(medians) < 34:
        return None

    sma5 = sum(medians[-5:]) / 5
    sma34 = sum(medians[-34:]) / 34

    ao = sma5 - sma34
    return ao