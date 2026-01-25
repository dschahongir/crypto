from datetime import datetime, timedelta
from config.settings import SIGNAL_COOLDOWN_MIN

cooldowns = {}

def can_send(symbol, minutes=SIGNAL_COOLDOWN_MIN):
    now = datetime.utcnow()

    if symbol in cooldowns:
        if now - cooldowns[symbol] < timedelta(minutes=minutes):
            return False

    cooldowns[symbol] = now
    return Truec