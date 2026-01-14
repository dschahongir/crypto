def detect_phase(bb, ao, rsi):
    # ФАЗА 1 — СЖАТИЕ
    if bb["width"] < 0.05 and rsi < 50:
        return "PREPARE"

    # ФАЗА 2 — ИМПУЛЬС БЕЗ ПОДТВЕРЖДЕНИЯ
    if bb["close"] > bb["ma"] and ao > 0:
        return "WAIT"

    # ФАЗА 3 — ВХОД
    if bb["close"] > bb["upper"] and ao > 0 and 40 <= rsi <= 65:
        return "ENTRY"

    return None