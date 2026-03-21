from django.conf import settings
from django.db import models

from creators.models import Creator


class Subscription(models.Model):
    """Подписка пользователя на автора"""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        CANCELED = "canceled", "Canceled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions", verbose_name="Пользователь")
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name="subscriptions", verbose_name="Автор")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, verbose_name="Статус подписки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания подписки")

    class Meta:
        unique_together = (("user", "creator"),)

    def __str__(self):
        return f"{self.user.email} -> {self.creator.display_name} ({self.status})"
