import requests
from config.settings import TELEGRAM_API_TOKEN, TELEGRAM_CHAT_ID

def send(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    })