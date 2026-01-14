def backtest(signals):
    wins = 0
    losses = 0

    for s in signals:
        entry = s["entry"]
        max_price = max(s["future_prices"])
        min_price = min(s["future_prices"])

        if max_price >= entry * 1.01:
            wins += 1
        elif min_price <= entry * 0.99:
            losses += 1

    total = wins + losses
    winrate = wins / total * 100 if total else 0

    return {
        "trades": total,
        "wins": wins,
        "losses": losses,
        "winrate": round(winrate, 2)
    }