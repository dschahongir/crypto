def too_late(rsi_value=None, gain_1h=None):
    if rsi_value and rsi_value > 70:
        return True
    if gain_1h and gain_1h >= 5:
        return True
    return False