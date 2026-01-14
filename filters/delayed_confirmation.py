def delayed_long_confirmation(
    price,
    prev_price,
    bb,
    atr,
    state,
    min_rebound_atr=0.3
):
    """
    min_rebound_atr = минимум отскока в ATR
    """

    # 1️⃣ касание нижней полосы
    if price <= bb["lower"]:
        state.touched_lower = True
        state.touch_price = price
        return False

    # 2️⃣ отскок вверх
    if state.touched_lower:
        rebound = price - state.touch_price

        if rebound >= atr * min_rebound_atr:
            state.confirmed = True

    # 3️⃣ закрепление выше middle
    if state.confirmed and prev_price < bb["middle"] and price > bb["middle"]:
        return True

    return False