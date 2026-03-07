from django.conf import settings
from django.db import models

from creators.models import Creator


class Subscription(models.Model):
    """Подписка пользователя на автора"""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        CANCELED = "canceled", "Canceled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name="subscribers")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("user", "creator"),)
