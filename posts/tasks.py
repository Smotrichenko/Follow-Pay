from celery import shared_task

from subscriptions.models import Subscription
from users.tasks import send_telegram_message_task

from .models import Post


@shared_task
def notify_subscribers_about_new_post(post_id):
    """Уведомляем всех подписчиков о новом посте автора"""

    post = Post.objects.select_related("creator").filter(id=post_id, is_published=True).first()
    if not post:
        return

    subs = Subscription.objects.filter(creator=post.creator, status=Subscription.Status.ACTIVE).values_list(
        "user_id", flat=True
    )

    text = f"🆕 У автора {post.creator.display_name} вышел новый пост: {post.title}"

    for user_id in subs:
        send_telegram_message_task.delay(user_id=user_id, text=text)
