def volume_delta(klines):
    bull = sum(k["volume"] for k in klines[-5:] if k["close"] > k["open"])
    bear = sum(k["volume"] for k in klines[-5:] if k["close"] < k["open"])

    return bull > bear * 1.3