import time
from datetime import datetime, timedelta
from data.binance_client import get_klines, get_price
from indicators.rsi import rsi_signal
from indicators.ema import ema_cross
from strategy.scorer import score_coin
from notifier.telegram import send

last_signal_time = None

def run_cycle(symbols):
    global last_signal_time
    scored = []

    for coin in symbols:
        signals = {}

        klines = get_klines(coin, "1h", 50)

        rsi = rsi_signal(klines)
        if rsi:
            signals[rsi[0]] = rsi[1]

        ema = ema_cross(klines)
        if ema:
            signals["EMA_BULLISH"] = True

        score, reasons = score_coin(coin, signals)

        if score >= 4:
            scored.append((coin, score, reasons))

    if scored:
        now = datetime.now()
        if not last_signal_time or now - last_signal_time > timedelta(minutes=30):
            msg = "<b>📊 SPOT BUY сигналы:</b>\n\n"
            for c, s, r in scored[:5]:
                msg += f"<b>{c}</b> — {s}\n" + "\n".join(r) + "\n\n"
            send(msg)
            last_signal_time = now