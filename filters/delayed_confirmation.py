def delayed_long_confirmation(
    price,
    klines_5m,  # Передаем свечи, чтобы посчитать локальный отскок
    bb,
    atr,
    state,
    min_rebound_atr=0.5
):
    """
    Логика:
    1. Касание нижней линии Боллинджера.
    2. Ожидание "зеленой" свечи, которая перекрывает падение или уверенно растет.
    """
    
    # 1️⃣ ФАЗА КАСАНИЯ: Цена пробила или коснулась нижней линии
    # Чуть расширяем зону касания (1.002), чтобы не пропускать касания "волосок в волосок"
    if price <= bb["lower"] * 1.002:
        state.touched_lower = True
        state.touch_price = price
        state.confirmed = False # Сбрасываем подтверждение при новом минимуме
        return False

    # 2️⃣ ФАЗА ОТСКОКА
    if state.touched_lower:
        # Проверяем последнюю закрытую свечу (текущая цена - это close последней 5м свечи)
        last_close = price
        last_open = klines_5m[-1]["open"]
        prev_close = klines_5m[-2]["close"]

        # Условие подтверждения:
        # 1. Цена выросла от дна касания
        rebound_value = last_close - state.touch_price
        
        # 2. Свеча зеленая (close > open)
        is_green = last_close > last_open

        # 3. Цена вернулась ВНУТРЬ канала (выше lower)
        back_in_channel = last_close > bb["lower"]

        # Триггер входа: Отскок на 0.5 ATR + Зеленая свеча + Возврат в канал
        if is_green and back_in_channel and rebound_value >= (atr * min_rebound_atr):
            return True

    return False