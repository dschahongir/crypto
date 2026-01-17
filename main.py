import asyncio
from contextlib import suppress
from threading import Thread
from flask import Flask
# 👇 ВОТ ЭТА СТРОКА ОЧЕНЬ ВАЖНА, БЕЗ НЕЕ БУДЕТ ОШИБКА
from runner.stream_manager import start_stream_manager
from notifier.telegram import send

app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 Crypto Bot V2 (Smart Logic) is Running!"

def run_flask():
    # Запускаем сервер на порту 3000
    # use_reloader=False важно, чтобы не запускалось два экземпляра бота
    app.run(host="0.0.0.0", port=3000, use_reloader=False)

def run_async_bot():
    # Отправляем приветственное сообщение
    send("🚀 <b>Бот успешно перезапущен!</b>\nЖду сигналы с рынка...") 
    
    # Запуск асинхронного цикла событий
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Запуск главной функции из stream_manager
    try:
        loop.run_until_complete(start_stream_manager())
    finally:
        with suppress(Exception):
            loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

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
    except Exception as e:
        print(f"❌ Критическая ошибка в main.py: {e}")