import asyncio
import json
import websockets
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from config.settings import WATCHLIST
from pipeline.processor import process_kline
from data.loader import fetch_initial_history

# Глобальное хранилище данных для всех монет
# Структура: { "BTCUSDT": [...свечи...], "ETHUSDT": [...] }
market_data = {}

BINANCE_WS = "wss://stream.binance.com:9443/ws"

async def socket_listener(symbol):
    """
    Слушает вебсокет для одной конкретной монеты
    """
    interval = "1m"
    stream = f"{symbol.lower()}@kline_{interval}"
    url = f"{BINANCE_WS}/{stream}"

    # 1. Сначала загружаем историю (чтобы бот сразу мог работать)
    history = fetch_initial_history(symbol, interval)
    market_data[symbol] = history

    while True:
        try:
            print(f"🎧 Подключение к потоку {symbol}...")
            async with websockets.connect(
                url,
                ping_interval=20,
                ping_timeout=20,
            ) as ws:
                print(f"✅ Поток {symbol} активен")
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    kline = data["k"]

                    # Обрабатываем только закрытые свечи
                    if kline["x"]:
                        new_candle = {
                            "open": float(kline["o"]),
                            "high": float(kline["h"]),
                            "low": float(kline["l"]),
                            "close": float(kline["c"]),
                            "volume": float(kline["v"]),
                            "close_time": kline["T"]
                        }

                        # Добавляем в список
                        current_list = market_data.get(symbol, [])
                        current_list.append(new_candle)

                        # Храним не более 200 свечей, чтобы не забивать память
                        if len(current_list) > 200:
                            current_list.pop(0)
                        
                        market_data[symbol] = current_list

                        # 🔥 ЗАПУСК МОЗГА (Pipeline)
                        process_kline(symbol, current_list)

        except (ConnectionClosedError, ConnectionClosedOK) as e:
            print(f"⚠️ Подключение {symbol} закрыто: {e}")
        except Exception as e:
            print(f"⚠️ Ошибка потока {symbol}: {e}")
        finally:
            # Небольшая пауза перед новым подключением, чтобы не спамить Binance
            await asyncio.sleep(5)

async def start_stream_manager():
    """
    Запускает задачи для всех монет из WATCHLIST
    """
    tasks = []
    print(f"🚀 Запуск менеджера потоков для {len(WATCHLIST)} монет...")
    
    for coin in WATCHLIST:
        tasks.append(socket_listener(coin))
    
    await asyncio.gather(*tasks)