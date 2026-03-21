import random

import requests
from django.conf import settings


def generate_login_code():
    """Генерирует код для входа"""
    return str(random.randint(1000, 9999))


def send_code_to_console(phone, code):
    """Выводим код в консоль"""
    print(f"[LOGIN CODE] phone={phone}, code={code}")


def send_telegram_message(chat_id: str, text: str) -> None:
    """Отправляет пользователю сообщения в Telegram"""
    if not settings.TELEGRAM_BOT_TOKEN or not chat_id:
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    try:
        requests.post(url, json=payload, timeout=10)
    except requests.RequestException:
        pass
