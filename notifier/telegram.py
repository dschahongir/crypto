# import requests
# from config.settings import TELEGRAM_API_TOKEN, TELEGRAM_CHAT_ID

# def send(message):
#     url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"
#     requests.post(url, json={
#         "chat_id": TELEGRAM_CHAT_ID,
#         "text": message,
#         "parse_mode": "HTML"
#     })


import requests
from threading import Thread
from config.settings import TELEGRAM_API_TOKEN, TELEGRAM_CHAT_ID

def _send_sync(message):
    """
    Внутренняя синхронная функция отправки.
    Мы прячем её внутрь, чтобы основной код её случайно не вызвал напрямую.
    """
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True  # Чтобы ссылки не разворачивались в пол-экрана
        }
        # timeout=5 важен! Если телеграм висит, мы не хотим ждать вечно.
        response = requests.post(url, json=payload, timeout=5)

        print("📨 Отправка сообщения в Telegram")
        
        if response.status_code != 200:
            print(f"⚠️ Ошибка отправки в Telegram: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети при отправке в Telegram: {e}")
    except Exception as e:
        print(f"❌ Неизвестная ошибка Telegram: {e}")

def send(message):
    """
    Публичная функция.
    Запускает отправку в фоновом потоке.
    Основной цикл бота НЕ БЛОКИРУЕТСЯ.
    """
    # daemon=True: поток закроется сам, если основной бот выключится
    thread = Thread(target=_send_sync, args=(message,), daemon=True)
    thread.start()
    print("📨 Запущен поток отправки сообщения в Telegram")