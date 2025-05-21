import requests

from core.config import settings

TOKEN = settings.telegram_bot_token
CHAT_ID = 5015947677 # 5015947677 433021023

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"


def send_new_car_request(message) -> None:
    try:

        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }

        response = requests.post(url, json=payload)

    except Exception as e:
        print(f"Ошибка {e}")


def send_proxy_error_request(message) -> None:
    try:

        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }

        print("send_proxy_error_request", payload)

        response = requests.post(url, json=payload)

    except Exception as e:
        print(f"Ошибка {e}")
