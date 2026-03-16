from celery import shared_task
from django.contrib.auth import get_user_model

from .services import send_telegram_message

User = get_user_model()


@shared_task
def send_telegram_message_task(user_id, text):
    """Фоновая задача для отправки уведомлений в Telegram"""

    user = User.objects.filter(id=user_id).first()
    if not user:
        return

    if not user.telegram_chat_id:
        return

    send_telegram_message(chat_id=str(user.telegram_chat_id), text=text)
