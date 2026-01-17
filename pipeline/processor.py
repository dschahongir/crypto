# from market_state.multitimeframe import multi_tf_check
# from core.cooldown import can_send

# from indicators.atr import calculate_atr
# from indicators.adaptive_bollinger import adaptive_bollinger

# from filters.volatility_filter import atr_filter
# from filters.delayed_confirmation import delayed_long_confirmation
# from filters.fake_breakout import fake_breakout_filter
# from filters.volume_delta import volume_delta

# from indicators.rsi import rsi
# from indicators.awesome import awesome_oscillator
# from market_state.phase_detector import detect_phase

# from strategy.confidence import calculate_confidence
# from state.signal_state import SignalState


# states = {}


# def aggregate_klines(klines, window):
#     """
#     Агрегация 1m → 5m / 15m
#     """
#     aggregated = []
#     if len(klines) < window:
#         return aggregated

#     for i in range(window - 1, len(klines)):
#         chunk = klines[i - window + 1 : i + 1]
#         aggregated.append({
#             "open": chunk[0]["open"],
#             "high": max(c["high"] for c in chunk),
#             "low": min(c["low"] for c in chunk),
#             "close": chunk[-1]["close"],
#             "volume": sum(c["volume"] for c in chunk),
#             "close_time": chunk[-1]["close_time"],
#         })

#     return aggregated


# def process_kline(symbol, klines):
#     """
#     Главный pipeline обработки свечей
#     """

#     # 🔹 Минимум данных
#     if len(klines) < 50:
#         return

#     # 🔹 Multi-Timeframe
#     klines_5m = aggregate_klines(klines, 5)
#     klines_15m = aggregate_klines(klines, 15)

#     if len(klines_5m) < 6 or len(klines_15m) < 6:
#         return

#     if not multi_tf_check(
#         data_1m=klines,
#         data_5m=klines_5m,
#         data_15m=klines_15m,
#     ):
#         return

#     # 🔹 Цена и closes
#     closes_5m = [k["close"] for k in klines_5m]
#     price = closes_5m[-1]
#     prev_price = closes_5m[-2]

#     # 🔹 ATR + волатильность
#     atr = calculate_atr(klines_5m)
#     if not atr_filter(atr, price):
#         return

#     # 🔹 Adaptive Bollinger (ЕДИНСТВЕННЫЙ)
#     bb = adaptive_bollinger(closes_5m, atr)
#     if bb is None:
#         return

#     # 🔹 State (память)
#     state = states.setdefault(symbol, SignalState())

#     # 🔹 Delayed confirmation (ОСНОВНОЙ ТРИГГЕР)
#     long_signal = delayed_long_confirmation(
#         price=price,
#         prev_price=prev_price,
#         bb=bb,
#         atr=atr,
#         state=state,
#     )

#     if not long_signal:
#         return

#     # 🔹 Дополнительные фильтры (ПОСЛЕ сигнала)
#     if not fake_breakout_filter(klines_5m, bb["upper"]):
#         return

#     if not volume_delta(klines_5m):
#         return

#     # 🔹 Старшие индикаторы ТОЛЬКО как фильтр
#     r = rsi([k["close"] for k in klines])
#     ao = awesome_oscillator(klines)

#     phase = detect_phase(bb, ao, r)
#     if phase != "ENTRY":
#         return

#     # 🔹 Cooldown ТОЛЬКО ПОСЛЕ ГОТОВОГО СИГНАЛА
#     if not can_send(symbol):
#         return

#     # 🔹 Confidence
#     confidence = calculate_confidence(
#         phase=phase,
#         ao=ao,
#         bb_width=(bb["upper"] - bb["lower"]) / bb["middle"]
#     )

#     # 🔹 Сброс состояния после сигнала
#     states[symbol] = SignalState()

#     # 🔹 ФИНАЛ
#     print(f"""
# 🟢 SPOT BUY SIGNAL
# Монета: {symbol}
# Цена: {price}
# ATR: {round(atr, 5)}
# Уверенность: {confidence}%
# """)



from market_state.multitimeframe import multi_tf_check
from core.cooldown import can_send

# Импорты индикаторов (Обрати внимание на правильные названия!)
from indicators.atr import calculate_atr
from indicators.adaptive_bollinger import adaptive_bollinger  # Исправлено имя
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
from notifier.telegram import send  # Функция отправки в Telegram

# Глобальное хранилище состояний монет
states = {}

def aggregate_klines(klines, window):
    """
    Превращает 1m свечи в 5m или 15m
    """
    aggregated = []
    if len(klines) < window:
        return aggregated

    # Берем данные шагами по window (например, по 5 штук)
    # Используем срез с шагом, чтобы брать каждую 5-ю закрытую свечу корректно
    # Упрощенная логика агрегации для последних свечей:
    
    # Для корректной агрегации нам нужно идти с конца
    # Но для скорости мы просто возьмем последние N*window свечей
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
    """
    Расчет умных уровней Stop Loss и Take Profit.
    SL ставим под нижнюю линию Боллинджера (поддержка).
    TP ставим с соотношением риск/прибыль 1:2 или 1:3.
    """
    # Стоп за нижнюю линию Боллинджера (немного ниже для страховки)
    stop_loss = bb_lower * 0.998 
    
    # Если стоп слишком близко (меньше 0.2%), отодвигаем его по ATR
    if (price - stop_loss) / price < 0.002:
        stop_loss = price - (atr * 1.5)

    risk = price - stop_loss
    
    # Тейк №1 (Консервативный) - 2 риска
    take_profit = price + (risk * 2.0)
    
    return stop_loss, take_profit

def process_kline(symbol, klines):
    """
    Главный МОЗГ. Анализирует свечи и принимает решение.
    """
    
    # 1. Нужно минимум 50 свечей для расчета индикаторов
    if len(klines) < 50:
        return

    # 2. Агрегация таймфреймов (1m -> 5m, 1m -> 15m)
    klines_5m = aggregate_klines(klines, 5)
    klines_15m = aggregate_klines(klines, 15)

    if len(klines_5m) < 20 or len(klines_15m) < 20:
        return

    # 3. Базовые переменные
    closes_5m = [k["close"] for k in klines_5m]
    price = closes_5m[-1]
    prev_price = closes_5m[-2]

    # 4. Проверка Трендов (Multi-Timeframe)
    # Если на 15м тренд вниз — не входим в Long
    if not multi_tf_check(klines, klines_5m, klines_15m):
        return

    # 5. ATR + Волатильность (Фильтр флэта)
    # Если рынок мертвый (мало движений) — не торгуем
    atr = calculate_atr(klines_5m)
    if not atr_filter(atr, price):
        return

    # 6. Адаптивный Боллинджер
    bb = adaptive_bollinger(closes_5m, atr)
    if bb is None:
        return

    # 7. Работа с состоянием (Память бота)
    state = states.setdefault(symbol, SignalState())

    # === ЛОГИКА ВХОДА ===
    # Функция delayed_long_confirmation ждет, пока цена коснется низа
    # и начнет отскакивать. Это фильтрует "падающие ножи".
    long_signal = delayed_long_confirmation(
        price=price,
        prev_price=prev_price,
        bb=bb,
        atr=atr,
        state=state,
    )

    if not long_signal:
        return

    # 8. Фильтры подтверждения (чтобы отсеять ложные пробои)
    if not fake_breakout_filter(klines_5m, bb["upper"]):
        return

    if not volume_delta(klines_5m):
        return

    # 9. Проверка фазы рынка (индикаторы AO и RSI)
    # rsi_signal возвращает кортеж, нам нужно значение
    r_val = 50 # дефолт
    r_data = rsi_signal([k["close"] for k in klines]) # Используем 1m RSI для точности
    if r_data:
        r_val = r_data[1]

    ao = awesome_oscillator(klines_5m)
    
    # Определяем фазу (Entry, Wait, Prepare)
    phase = detect_phase(bb, ao, r_val)
    
    if phase != "ENTRY":
        return

    # 10. Cooldown (чтобы не спамить сигналами по одной монете)
    if not can_send(symbol):
        return

    # 11. Расчет уверенности (0-100%)
    confidence = calculate_confidence(
        phase=phase,
        ao=ao,
        bb_width=(bb["upper"] - bb["lower"]) / bb["middle"]
    )
    
    # 🔥 ФИЛЬТР КАЧЕСТВА: Если уверенность низкая, пропускаем
    if confidence < 70:
        return

    # 12. Расчет TP и SL
    stop_loss, take_profit = calculate_tp_sl(price, bb["lower"], atr)
    
    # Сбрасываем состояние после успешного сигнала
    states[symbol] = SignalState()

    # 13. ОТПРАВКА СИГНАЛА
    risk_pct = round(((price - stop_loss) / price) * 100, 2)
    profit_pct = round(((take_profit - price) / price) * 100, 2)

    message = (
        f"<b>🚀 SPOT BUY SIGNAL: {symbol}</b>\n\n"
        f"💰 <b>Вход:</b> {price}\n"
        f"🎯 <b>Take Profit:</b> {round(take_profit, 4)} (+{profit_pct}%)\n"
        f"🛑 <b>Stop Loss:</b> {round(stop_loss, 4)} (-{risk_pct}%)\n\n"
        f"📊 <b>Анализ:</b>\n"
        f"— ATR (Волатильность): {round(atr, 5)}\n"
        f"— Уверенность ИИ: {confidence}%\n"
        f"— RSI: {round(r_val, 2)}\n"
        f"<i>⚠️ Соблюдайте риск-менеджмент!</i>"
    )
    
    print(f"✅ Сигнал отправлен по {symbol}") # Лог в консоль
    send(message) # Лог в Телеграм