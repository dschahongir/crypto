# from market_state.multitimeframe import multi_tf_check
# from core.cooldown import can_send
# from indicators.atr import calculate_atr
# from indicators.adaptive_bollinger import adaptive_bollinger
# from indicators.rsi import rsi_signal
# from filters.volatility_filter import atr_filter
# from filters.delayed_confirmation import delayed_long_confirmation
# from filters.fake_breakout import fake_breakout_filter
# from filters.volume_delta import volume_delta
# from indicators.awesome import awesome_oscillator
# from market_state.phase_detector import detect_phase
# from strategy.confidence import calculate_confidence
# from state.signal_state import SignalState
# from notifier.telegram import send

# states = {}

# def aggregate_klines(klines, window):
#     if len(klines) < window: return []
#     count = len(klines) // window
#     start_index = len(klines) - (count * window)
#     clean_klines = klines[start_index:]
    
#     aggregated = []
#     for i in range(0, len(clean_klines), window):
#         chunk = clean_klines[i : i + window]
#         agg_candle = {
#             "open": chunk[0]["open"],
#             "high": max(c["high"] for c in chunk),
#             "low": min(c["low"] for c in chunk),
#             "close": chunk[-1]["close"],
#             "volume": sum(c["volume"] for c in chunk),
#             "close_time": chunk[-1]["close_time"],
#         }
#         aggregated.append(agg_candle)
#     return aggregated

# def calculate_tp_sl(price, bb_lower, atr):
#     stop_loss = bb_lower - (atr * 0.5) # Чуть ниже Bollinger
#     # Защита от слишком короткого стопа
#     if (price - stop_loss) / price < 0.004:
#         stop_loss = price - (atr * 2.0)

#     risk = price - stop_loss
#     take_profit = price + (risk * 2.0) # Риск/Прибыль 1:2
#     return stop_loss, take_profit

# def process_kline(symbol, klines):
#     if len(klines) < 55: return

#     # 1. Агрегация (Смотрим на 5m для чистоты сигнала)
#     klines_5m = aggregate_klines(klines, 5)
#     klines_15m = aggregate_klines(klines, 15)
    
#     if len(klines_5m) < 35: return # Нужно 35 свечей для AO

#     closes_5m = [k["close"] for k in klines_5m]
#     price = closes_5m[-1]

#     # 2. Индикаторы
#     atr = calculate_atr(klines_5m)
#     bb = adaptive_bollinger(closes_5m, atr)
#     rsi_val = rsi_signal([k["close"] for k in klines]) 
    
#     # Получаем ДВА значения AO (текущий и прошлый)
#     ao_curr, ao_prev = awesome_oscillator(klines_5m)

#     if not bb or not atr or ao_curr is None: return

#     # 3. Фильтры
#     if not multi_tf_check(klines, klines_5m, klines_15m): 
#         # Разрешаем вход против тренда, если RSI экстремально низкий (отскок дохлой кошки)
#         if rsi_val > 25: return 

#     if not atr_filter(atr, price): return

#     # 4. Логика входа (Стратегия JustUncleL)
#     phase = detect_phase(bb, ao_curr, ao_prev, rsi_val, price)
    
#     if phase != "ENTRY":
#         return

#     # 5. Доп. подтверждения
#     if not volume_delta(klines_5m): return
#     if not can_send(symbol): return

#     # 6. Уверенность
#     confidence = calculate_confidence(phase, ao_curr, (bb["upper"] - bb["lower"]) / bb["middle"])
#     if confidence < 75: return

#     # 7. Расчет сделки
#     sl, tp = calculate_tp_sl(price, bb["lower"], atr)
    
#     # Ссылка на график
#     tv_link = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}"

#     # Формирование красивого сообщения
#     risk_pct = round(((price - sl) / price) * 100, 2)
#     profit_pct = round(((tp - price) / price) * 100, 2)

#     msg = (
#         f"⚠️ <i>Дисклеймер: Бот не дает финансовых советов. DYOR.</i>\n\n"
#         f"🟢 <b>LONG: {symbol}</b>\n"
#         f"───────────────\n"
#         f"📥 <b>Вход:</b> {price}\n"
#         f"🎯 <b>Take Profit:</b> {round(tp, 4)} (+{profit_pct}%)\n"
#         f"🛑 <b>Stop Loss:</b> {round(sl, 4)} (-{risk_pct}%)\n"
#         f"───────────────\n"
#         f"🤖 <b>Уверенность:</b> {confidence}%\n"
#         f"📊 <b>Индикаторы:</b> RSI {rsi_val} | AO Green\n"
#         f"🔗 <a href=\"{tv_link}\">Открыть на TradingView</a>"
#     )
    
#     print(f"✅ SIGNAL: {symbol} (AO Flip)")
#     send(msg)














from market_state.multitimeframe import multi_tf_check
from core.cooldown import can_send
from indicators.atr import calculate_atr
from indicators.adaptive_bollinger import adaptive_bollinger
from indicators.rsi import rsi_signal
from filters.volatility_filter import atr_filter
from filters.delayed_confirmation import delayed_long_confirmation
from filters.fake_breakout import fake_breakout_filter
from filters.volume_delta import volume_delta
from indicators.awesome import awesome_oscillator
from market_state.phase_detector import detect_phase
from strategy.confidence import calculate_confidence
from state.signal_state import SignalState
from notifier.telegram import send

states = {}

def aggregate_klines(klines, count):
    """
    Агрегация свечей.
    Если база 15m:
    count=4 -> получаем 1h
    count=16 -> получаем 4h
    """
    if len(klines) < count: return []
    
    # Срезаем лишнее с начала, чтобы делилось ровно
    needed_len = (len(klines) // count) * count
    trimmed_klines = klines[-needed_len:]
    
    aggregated = []
    for i in range(0, len(trimmed_klines), count):
        chunk = trimmed_klines[i : i + count]
        agg_candle = {
            "open": chunk[0]["open"],
            "high": max(c["high"] for c in chunk),
            "low": min(c["low"] for c in chunk),
            "close": chunk[-1]["close"],
            "volume": sum(c["volume"] for c in chunk),
            "close_time": chunk[-1]["close_time"],
        }
        aggregated.append(agg_candle)
    return aggregated

def calculate_tp_sl(price, bb_lower, atr):
    # === НАСТРОЙКИ ДЛЯ INTRADAY (Сделка на день) ===
    
    # Stop Loss: Более широкий, чтобы пережить шум
    # Ставим под Bollinger Band с запасом 0.5 ATR
    stop_loss = bb_lower - (atr * 0.5) 
    
    # Защита: Если стоп слишком близко (<1%), отодвигаем принудительно
    if (price - stop_loss) / price < 0.01:
        stop_loss = price - (atr * 2.5)

    risk = price - stop_loss
    
    # Take Profit: Целимся высоко. 
    # Риск/Прибыль 1:3 (на 1$ риска хотим 3$ прибыли)
    take_profit = price + (risk * 3.0) 
    
    return stop_loss, take_profit

def process_kline(symbol, klines):
    # klines здесь - это уже 15-минутки
    if len(klines) < 60: return

    # 1. Формируем Старшие Таймфреймы
    # 4 свечи по 15м = 1 Час (Рабочий график)
    klines_1h = aggregate_klines(klines, 4)
    # 16 свечей по 15м = 4 Часа (Глобальный тренд)
    klines_4h = aggregate_klines(klines, 16)
    
    if len(klines_1h) < 35 or len(klines_4h) < 20: return 

    # Мы принимаем решение по 1-ЧАСОВОМУ графику
    current_tf = klines_1h 
    
    closes = [k["close"] for k in current_tf]
    price = closes[-1]

    # 2. Индикаторы (по 1h)
    atr = calculate_atr(current_tf)
    bb = adaptive_bollinger(closes, atr)
    
    # RSI тоже смотрим на 15м и 1ч, возьмем среднее или 1ч для надежности
    rsi_val = rsi_signal([k["close"] for k in current_tf]) 
    
    # AO на 1h
    ao_curr, ao_prev = awesome_oscillator(current_tf)

    if not bb or not atr or ao_curr is None: return

    # 3. Фильтр Тренда (Смотрим на 4h)
    # Если на 4h тренд вниз - лонговать опасно, даже если на 1h все красиво
    # Передаем: base(15m), work(1h), trend(4h)
    if not multi_tf_check(klines, klines_1h, klines_4h): 
        # Исключение: Супер перепроданность на 1h
        if rsi_val > 30: return 

    # 4. Фильтр волатильности
    if not atr_filter(atr, price): return

    # 5. Логика входа (Стратегия JustUncleL на 1h)
    phase = detect_phase(bb, ao_curr, ao_prev, rsi_val, price)
    
    if phase != "ENTRY":
        return

    # 6. Доп. подтверждения
    # Объем смотрим на 1h
    if not volume_delta(current_tf): return
    if not can_send(symbol): return

    # 7. Уверенность
    confidence = calculate_confidence(phase, ao_curr, (bb["upper"] - bb["lower"]) / bb["middle"])
    
    # Для Дневных сделок требования выше
    if confidence < 80: return

    # 8. Расчет сделки
    sl, tp = calculate_tp_sl(price, bb["lower"], atr)
    
    tv_link = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}&interval=60"

    risk_pct = round(((price - sl) / price) * 100, 2)
    profit_pct = round(((tp - price) / price) * 100, 2)

    msg = (
        f"⚠️ <i>Medium-Term Signal (1-24h)</i>\n\n"
        f"💎 <b>LONG: {symbol} (1H Chart)</b>\n"
        f"───────────────\n"
        f"📥 <b>Вход:</b> {price}\n"
        f"🎯 <b>TP (Target):</b> {round(tp, 4)} (+{profit_pct}%)\n"
        f"🛑 <b>SL (Safety):</b> {round(sl, 4)} (-{risk_pct}%)\n"
        f"───────────────\n"
        f"🌊 <b>Тренд 4H:</b> UP\n"
        f"📊 <b>RSI 1H:</b> {rsi_val}\n"
        f"🔗 <a href=\"{tv_link}\">График 1H</a>"
    )
    
    print(f"✅ INTRADAY SIGNAL: {symbol}")
    send(msg)