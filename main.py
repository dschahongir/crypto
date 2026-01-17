# import time
# from flask import Flask
# from threading import Thread
# from runner.bot_loop import run_cycle
# from config.settings import WATCHLIST, SCAN_INTERVAL_SEC

# app = Flask(__name__)

# @app.route("/")
# def home():
#     return "Bot is running"

# def bot():
#     while True:
#         run_cycle(WATCHLIST)
#         time.sleep(SCAN_INTERVAL_SEC)

# if __name__ == "__main__":
#     Thread(target=bot, daemon=True).start()
#     app.run(host="0.0.0.0", port=3000)


import asyncio
from threading import Thread
from flask import Flask
# Обрати внимание: мы импортируем start_stream_manager, а НЕ run_cycle
from runner.stream_manager import start_stream_manager
from notifier.telegram import send

app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 Crypto Bot V2 (Smart Logic) is Running!"

def run_flask():
    # Запускаем сервер на порту 3000
    app.run(host="0.0.0.0", port=3000, use_reloader=False)

def run_async_bot():
    send("🚀 <b>Бот успешно перезапущен!</b>\nЖду сигналы с рынка...") # <--- ДОБАВЬ ЭТУ СТРОКУ
    # Запуск асинхронного цикла событий
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_stream_manager())

if __name__ == "__main__":
    print("🟢 Инициализация системы...")

    # 1. Запуск веб-сервера (в отдельном потоке)
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 2. Запуск основной логики бота (блокирует основной поток)
    try:
        run_async_bot()
    except KeyboardInterrupt:
        print("🛑 Бот остановлен пользователем")