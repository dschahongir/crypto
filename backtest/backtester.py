def backtest(signals):
    wins = 0
    losses = 0

    for s in signals:
        entry = s["entry"]
        tp = s["tp"]
        sl = s["sl"]
        prices = s["future_prices"] # Список цен после входа

        for p in prices:
            if p >= tp:
                wins += 1
                break
            if p <= sl:
                losses += 1
                break

    total = wins + losses
    winrate = wins / total * 100 if total else 0

    return {
        "trades": total,
        "wins": wins,
        "losses": losses,
        "winrate": round(winrate, 2)
    }