def can_enter(price_change_pct, rsi):
    if price_change_pct > 4:
        return False
    if rsi > 70:
        return False
    return True