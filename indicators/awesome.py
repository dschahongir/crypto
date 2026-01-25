def awesome_oscillator(klines):
    """
    Возвращает кортеж (текущий AO, предыдущий AO).
    Нужно для определения смены цвета гистограммы.
    """
    if len(klines) < 35:
        return None, None

    medians = [(k["high"] + k["low"]) / 2 for k in klines]

    # Вспомогательная функция SMA
    def sma(data, period):
        return sum(data[-period:]) / period

    # Текущий AO
    ao_curr = sma(medians, 5) - sma(medians, 34)

    # Предыдущий AO (сдвигаем срез на -1)
    prev_medians = medians[:-1]
    ao_prev = sma(prev_medians, 5) - sma(prev_medians, 34)

    return ao_curr, ao_prev