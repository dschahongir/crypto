def fake_breakout_filter(klines, bb_middle):
    last = klines[-1]
    prev = klines[-2]

    # должны быть выше middle (подтверждение отскока)
    if last["close"] < bb_middle:
        return False

    avg_volume = sum(k["volume"] for k in klines[-20:]) / 20
    if last["volume"] < avg_volume * 1.1:
        return False

    change = (last["close"] - prev["close"]) / prev["close"] * 100
    if change > 2.0:
        return False

    return True