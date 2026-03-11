from django.conf import settings
from django.db import models

from creators.models import Creator


class Payment(models.Model):
    """Модель оплаты подписки"""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments", verbose_name="Пользователь"
    )
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name="payments", verbose_name="Автор")
    stripe_session_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="Статус оплаты"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")

    def __str__(self):
        return f"Payment #{self.id} | {self.user.email} -> {self.creator.display_name}"
