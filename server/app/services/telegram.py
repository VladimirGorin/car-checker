import requests

from core.config import settings

TOKEN = settings.telegram_bot_token
CHAT_ID = 5015947677


def send_new_car_request(message) -> None:
    try:

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }

        response = requests.post(url, json=payload)

    except Exception as e:
        print(f"Ошибка {e}")
