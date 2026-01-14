import asyncio
from core.ws_client import kline_socket
from pipeline.processor import process_kline

SYMBOL = "BTCUSDT"
klines = []


def on_kline(k):
    klines.append(k)
    if len(klines) > 100:
        klines.pop(0)
    process_kline(SYMBOL, klines)


async def main():
    await kline_socket(SYMBOL, "1m", on_kline)

asyncio.run(main())