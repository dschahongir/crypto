def fake_breakout_filter(klines, bb_upper):
    last = klines[-1]
    prev = klines[-2]

    # цена вернулась под BB → фейк
    if last["close"] < bb_upper:
        return False

    # объём не подтвердил
    avg_volume = sum(k["volume"] for k in klines[-20:]) / 20
    if last["volume"] < avg_volume * 1.2:
        return False

    # слишком резкий рост → памп
    change = (last["close"] - prev["close"]) / prev["close"] * 100
    if change > 3:
        return False

    return True