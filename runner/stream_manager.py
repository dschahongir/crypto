import asyncio
import json
import websockets
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from config.settings import WATCHLIST
from pipeline.processor import process_kline
from data.loader import fetch_initial_history

# Глобальное хранилище данных
market_data = {}

BINANCE_WS = "wss://stream.binance.com:9443/ws"

async def socket_listener(symbol):
    interval = "1m"
    stream = f"{symbol.lower()}@kline_{interval}"
    url = f"{BINANCE_WS}/{stream}"

    # Загрузка истории
    history = fetch_initial_history(symbol, interval)
    market_data[symbol] = history

    while True:
        try:
            print(f"🎧 Подключение к потоку {symbol}...")
            async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
                print(f"✅ Поток {symbol} активен")
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    kline = data["k"]

                    if kline["x"]:  # Свеча закрыта
                        new_candle = {
                            "open": float(kline["o"]),
                            "high": float(kline["h"]),
                            "low": float(kline["l"]),
                            "close": float(kline["c"]),
                            "volume": float(kline["v"]),
                            "close_time": kline["T"]
                        }

                        current_list = market_data.get(symbol, [])
                        
                        # 🔥 ИСПРАВЛЕНИЕ: Добавляем ТОЛЬКО ОДИН РАЗ
                        current_list.append(new_candle)

                        MAX_CANDLES = 1000
                        if len(current_list) > MAX_CANDLES:
                            current_list.pop(0)
                        
                        market_data[symbol] = current_list

                        # Запуск анализа
                        process_kline(symbol, current_list)

        except (ConnectionClosedError, ConnectionClosedOK):
            print(f"⚠️ Соединение {symbol} разорвано, перезапуск...")
        except Exception as e:
            print(f"⚠️ Ошибка потока {symbol}: {e}")
        finally:
            await asyncio.sleep(5)

async def start_stream_manager():
    tasks = []
    print(f"🚀 Запуск потоков для {len(WATCHLIST)} монет...")
    # Ограничиваем кол-во одновременных соединений (Semaphores не нужны для websockets, но лучше запускать пачками если монет 50+)
    for coin in WATCHLIST:
        tasks.append(socket_listener(coin))
    
    await asyncio.gather(*tasks)