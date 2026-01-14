from market_state.multitimeframe import multi_tf_check
from core.cooldown import can_send

from indicators.atr import calculate_atr
from indicators.bollinger_adaptive import adaptive_bollinger

from filters.volatility_filter import atr_filter
from filters.delayed_confirmation import delayed_long_confirmation
from filters.fake_breakout import fake_breakout_filter
from filters.volume_delta import volume_delta

from indicators.rsi import rsi
from indicators.awesome import awesome_oscillator
from market_state.phase_detector import detect_phase

from strategy.confidence import calculate_confidence
from state.signal_state import SignalState


states = {}


def aggregate_klines(klines, window):
    """
    Агрегация 1m → 5m / 15m
    """
    aggregated = []
    if len(klines) < window:
        return aggregated

    for i in range(window - 1, len(klines)):
        chunk = klines[i - window + 1 : i + 1]
        aggregated.append({
            "open": chunk[0]["open"],
            "high": max(c["high"] for c in chunk),
            "low": min(c["low"] for c in chunk),
            "close": chunk[-1]["close"],
            "volume": sum(c["volume"] for c in chunk),
            "close_time": chunk[-1]["close_time"],
        })

    return aggregated


def process_kline(symbol, klines):
    """
    Главный pipeline обработки свечей
    """

    # 🔹 Минимум данных
    if len(klines) < 50:
        return

    # 🔹 Multi-Timeframe
    klines_5m = aggregate_klines(klines, 5)
    klines_15m = aggregate_klines(klines, 15)

    if len(klines_5m) < 6 or len(klines_15m) < 6:
        return

    if not multi_tf_check(
        data_1m=klines,
        data_5m=klines_5m,
        data_15m=klines_15m,
    ):
        return

    # 🔹 Цена и closes
    closes_5m = [k["close"] for k in klines_5m]
    price = closes_5m[-1]
    prev_price = closes_5m[-2]

    # 🔹 ATR + волатильность
    atr = calculate_atr(klines_5m)
    if not atr_filter(atr, price):
        return

    # 🔹 Adaptive Bollinger (ЕДИНСТВЕННЫЙ)
    bb = adaptive_bollinger(closes_5m, atr)
    if bb is None:
        return

    # 🔹 State (память)
    state = states.setdefault(symbol, SignalState())

    # 🔹 Delayed confirmation (ОСНОВНОЙ ТРИГГЕР)
    long_signal = delayed_long_confirmation(
        price=price,
        prev_price=prev_price,
        bb=bb,
        atr=atr,
        state=state,
    )

    if not long_signal:
        return

    # 🔹 Дополнительные фильтры (ПОСЛЕ сигнала)
    if not fake_breakout_filter(klines_5m, bb["upper"]):
        return

    if not volume_delta(klines_5m):
        return

    # 🔹 Старшие индикаторы ТОЛЬКО как фильтр
    r = rsi([k["close"] for k in klines])
    ao = awesome_oscillator(klines)

    phase = detect_phase(bb, ao, r)
    if phase != "ENTRY":
        return

    # 🔹 Cooldown ТОЛЬКО ПОСЛЕ ГОТОВОГО СИГНАЛА
    if not can_send(symbol):
        return

    # 🔹 Confidence
    confidence = calculate_confidence(
        phase=phase,
        ao=ao,
        bb_width=(bb["upper"] - bb["lower"]) / bb["middle"]
    )

    # 🔹 Сброс состояния после сигнала
    states[symbol] = SignalState()

    # 🔹 ФИНАЛ
    print(f"""
🟢 SPOT BUY SIGNAL
Монета: {symbol}
Цена: {price}
ATR: {round(atr, 5)}
Уверенность: {confidence}%
""")