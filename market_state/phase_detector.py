def detect_phase(bb, ao_curr, ao_prev, rsi, price):
    """
    Стратегия Bollinger AwesomeAlert + R:
    1. Цена была или находится у нижней ленты (Squeeze/Touch).
    2. Импульс AO разворачивается вверх (Красный -> Зеленый).
    3. RSI в безопасной зоне.
    """
    
    # 1. Проверка Боллинджера
    # Цена ниже нижней линии или очень близко к ней (зона покупки)
    # Либо цена только что вернулась внутрь канала
    is_at_bottom = price <= bb["lower"] * 1.015

    # 2. Проверка Awesome Oscillator (AO)
    # "Saucer" или разворот: Предыдущий был ниже (падал), Текущий выше (растет)
    # Это означает, что гистограмма стала ЗЕЛЕНОЙ
    ao_momentum_up = ao_curr > ao_prev

    # 3. Логика входа
    # Если мы на дне И импульс пошел вверх И RSI не перекуплен
    if is_at_bottom and ao_momentum_up:
        if rsi < 60: # Фильтр: не входим, если RSI уже улетел
            return "ENTRY"
            
    # Дополнительный сценарий: "Zero Line Cross" (Пересечение нуля снизу вверх)
    # Если AO пересек 0 снизу вверх, и мы не у верхней границы
    if ao_prev < 0 and ao_curr > 0 and price < bb["middle"]:
        return "ENTRY"

    return "WAIT"