def trend_up(closes):
    return closes[-1] > closes[-3] > closes[-6]


def multi_tf_check(data_1m, data_5m, data_15m):
    """
    data_* = список свечей [{open, high, low, close, volume}]
    """

    closes_1m = [c["close"] for c in data_1m]
    closes_5m = [c["close"] for c in data_5m]
    closes_15m = [c["close"] for c in data_15m]

    # 15m — ГЛАВНЫЙ ФИЛЬТР
    if not trend_up(closes_15m):
        return False

    # 5m — локальный тренд
    if not trend_up(closes_5m):
        return False

    # 1m — разрешение на вход
    if closes_1m[-1] < closes_1m[-2]:
        return False

    return True