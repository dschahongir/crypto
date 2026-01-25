def volume_delta(klines, ratio=1.15):
    bull = sum(k["volume"] for k in klines[-5:] if k["close"] > k["open"])
    bear = sum(k["volume"] for k in klines[-5:] if k["close"] < k["open"])

    return bull > bear * ratiode