from datetime import datetime, timedelta

cooldowns = {}

def can_send(symbol, minutes=45):
    now = datetime.utcnow()

    if symbol in cooldowns:
        if now - cooldowns[symbol] < timedelta(minutes=minutes):
            return False

    cooldowns[symbol] = now
    return True