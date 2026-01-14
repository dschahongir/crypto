import asyncio
import json
import websockets

BINANCE_WS = "wss://stream.binance.com:9443/ws"

async def kline_socket(symbol, interval, on_kline):
    stream = f"{symbol.lower()}@kline_{interval}"
    url = f"{BINANCE_WS}/{stream}"

    async with websockets.connect(url) as ws:
        async for msg in ws:
            data = json.loads(msg)
            kline = data["k"]

            # используем ТОЛЬКО закрытые свечи
            if kline["x"]:
                on_kline({
                    "open": float(kline["o"]),
                    "high": float(kline["h"]),
                    "low": float(kline["l"]),
                    "close": float(kline["c"]),
                    "volume": float(kline["v"]),
                    "close_time": kline["T"]
                })