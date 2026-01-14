def calculate_ema(prices, period):
    ema = [prices[0]]
    k = 2 / (period + 1)
    for price in prices[1:]:
        ema.append(price * k + ema[-1] * (1 - k))
    return ema

def ema_cross(klines):
    closes = [float(k[4]) for k in klines]
    if len(closes) < 21:
        return None

    ema9 = calculate_ema(closes, 9)
    ema21 = calculate_ema(closes, 21)

    if ema9[-2] < ema21[-2] and ema9[-1] > ema21[-1]:
        return "BULLISH"
    return None