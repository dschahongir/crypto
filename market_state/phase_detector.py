def detect_phase(bb, ao, rsi):
    # хотим входить после возврата выше middle/ma, не требуя пробоя upper

    # подготовка: были внизу и rsi низкий
    if bb["close"] <= bb["lower"] and rsi < 40:
        return "PREPARE"

    # ожидание: цена вернулась выше lower, но ещё не закрепилась
    if bb["lower"] < bb["close"] < bb["ma"] and ao >= 0:
        return "WAIT"

    # вход: закрепились выше ma + норм rsi
    if bb["close"] > bb["ma"] and ao > 0 and 35 <= rsi <= 65:
        return "ENTRY"

    return None