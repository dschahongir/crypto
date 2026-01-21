from market_state.multitimeframe import multi_tf_check
from core.cooldown import can_send

# Импорты индикаторов
from indicators.atr import calculate_atr
from indicators.adaptive_bollinger import adaptive_bollinger
from indicators.rsi import rsi_signal

# Импорты фильтров
from filters.volatility_filter import atr_filter
from filters.delayed_confirmation import delayed_long_confirmation
from filters.fake_breakout import fake_breakout_filter
from filters.volume_delta import volume_delta

# Другие модули
from indicators.awesome import awesome_oscillator
from market_state.phase_detector import detect_phase
from strategy.confidence import calculate_confidence
from state.signal_state import SignalState
from notifier.telegram import send

# Глобальное хранилище состояний монет
states = {}

def aggregate_klines(klines, window):
    """
    Превращает 1m свечи в 5m или 15m
    """
    aggregated = []
    if len(klines) < window:
        return aggregated

    needed_len = (len(klines) // window) * window
    trimmed_klines = klines[-needed_len:]
    
    for i in range(0, len(trimmed_klines), window):
        chunk = trimmed_klines[i : i + window]
        aggregated.append({
            "open": chunk[0]["open"],
            "high": max(c["high"] for c in chunk),
            "low": min(c["low"] for c in chunk),
            "close": chunk[-1]["close"],
            "volume": sum(c["volume"] for c in chunk),
            "close_time": chunk[-1]["close_time"],
        })

    return aggregated

def calculate_tp_sl(price, bb_lower, atr):
    stop_loss = bb_lower * 0.998 
    if (price - stop_loss) / price < 0.002:
        stop_loss = price - (atr * 1.5)
    risk = price - stop_loss
    take_profit = price + (risk * 2.0)
    return stop_loss, take_profit

def process_kline(symbol, klines):
    """
    Главный МОЗГ
    """
    
    # 1. Минимум данных
    if len(klines) < 50:
        return

    # 2. Агрегация
    klines_5m = aggregate_klines(klines, 5)
    klines_15m = aggregate_klines(klines, 15)

    if len(klines_5m) < 20 or len(klines_15m) < 20:
        return

    # 3. Базовые переменные
    closes_5m = [k["close"] for k in klines_5m]
    price = closes_5m[-1]
    prev_price = closes_5m[-2]

    # Подсчет индикаторов (нужны для лога)
    r_val = 50
    r_data = rsi_signal([k["close"] for k in klines])
    if r_data:
        r_val = r_data[1]
    
    atr = calculate_atr(klines_5m)
    bb = adaptive_bollinger(closes_5m, atr)

    # ===============================================
    # 👀 MONITOR (ВСТАВИЛИ СЮДА, ЧТОБЫ ВИДЕТЬ ВСЕГДА)
    # ===============================================
    if symbol in ["DOTUSDT", "ETHUSDT", "ADAUSDT", "XRPUSDT", "LTCUSDT", "BCHUSDT", "BTCUSDT"]:
        # Проверяем статус тренда просто для вывода в лог
        is_trend_ok = multi_tf_check(klines, klines_5m, klines_15m)
        trend_status = "UP 🟢" if is_trend_ok else "DOWN 🔴"
        
        # Защита если BB еще не рассчитался
        bb_low_str = round(bb['lower'], 2) if bb else "Calc..."
        
        print(f"👀 MONITOR: {symbol} | Price: {price} | RSI: {round(r_val, 2)} | Trend: {trend_status} | Ждем ниже: {bb_low_str}")
    # ===============================================

    # 4. Проверка Трендов (Multi-Timeframe)
    if not multi_tf_check(klines, klines_5m, klines_15m):
        return

    # 5. ATR + Волатильность
    if not atr_filter(atr, price):
        return

    # 6. Боллинджер
    if bb is None:
        return

    # 7. Работа с состоянием
    state = states.setdefault(symbol, SignalState())

    # === ЛОГИКА ВХОДА ===
    long_signal = delayed_long_confirmation(
        price=price,
        prev_price=prev_price,
        bb=bb,
        atr=atr,
        state=state,
    )

    if not long_signal:
        return

    # 8. Фильтры
    if not fake_breakout_filter(klines_5m, bb["middle"]):
        return

    if not volume_delta(klines_5m):
        return

    # 9. Фаза рынка
    if r_val > 70: # Отсекаем перекупленность
        return

    ao = awesome_oscillator(klines_5m)
    
    # Исправил вызов функции (убрал лишний аргумент price, если в phase_detector его нет)
    phase = detect_phase(bb, ao, r_val)

    if phase != "ENTRY":
        return

    # 10. Cooldown
    if not can_send(symbol):
        return

    # 11. Уверенность
    confidence = calculate_confidence(
        phase=phase,
        ao=ao,
        bb_width=(bb["upper"] - bb["lower"]) / bb["middle"]
    )
    
    if confidence < 65:
        return

    # 12. TP / SL
    stop_loss, take_profit = calculate_tp_sl(price, bb["lower"], atr)
    
    states[symbol] = SignalState()

    # 13. ОТПРАВКА
    risk_pct = round(((price - stop_loss) / price) * 100, 2)
    profit_pct = round(((take_profit - price) / price) * 100, 2)

    message = (
        f"<b>🚀 SPOT BUY SIGNAL: {symbol}</b>\n\n"
        f"💰 <b>Вход:</b> {price}\n"
        f"🎯 <b>Take Profit:</b> {round(take_profit, 4)} (+{profit_pct}%)\n"
        f"🛑 <b>Stop Loss:</b> {round(stop_loss, 4)} (-{risk_pct}%)\n\n"
        f"📊 <b>Анализ:</b>\n"
        f"— ATR: {round(atr, 5)}\n"
        f"— Уверенность: {confidence}%\n"
        f"— RSI: {round(r_val, 2)}\n"
        f"<i>⚠️ Риск-менеджмент обязателен!</i>"
    )
    
    print(f"✅✅✅ СИГНАЛ ОТПРАВЛЕН ПО {symbol} ✅✅✅")
    send(message)