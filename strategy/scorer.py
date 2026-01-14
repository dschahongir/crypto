def score_coin(coin, signals):
    score = 0
    reasons = []

    if "RSI_OVERSOLD" in signals:
        score += 2
        reasons.append("RSI перепродан")

    if "EMA_BULLISH" in signals:
        score += 2
        reasons.append("EMA бычий крест")

    if "VOLUME_SPIKE" in signals:
        score += 2
        reasons.append("Всплеск объёма")

    if "CONSOLIDATION" in signals:
        score += 1
        reasons.append("Консолидация")

    return score, reasons