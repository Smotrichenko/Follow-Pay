import requests
from django.conf import settings


def send_telegram_message(chat_id: str, text: str) -> None:
    """Отправляет пользователю сообщения в Telegram"""
    if not settings.TELEGRAM_BOT_TOKEN or not chat_id:
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload, timeout=10)
