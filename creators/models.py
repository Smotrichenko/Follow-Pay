from django.db import models
from django.conf import settings


class Creator(models.Model):
    """Автор - пользователь, который может публиковать посты и иметь подписчиков"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="creator_profile",
        verbose_name="Владелец профиля автора",
    )
    display_name = models.CharField(max_length=150, verbose_name="Имя автора, которое видят пользователи")

    subscription_price_rub = models.PositiveIntegerField(default=500, verbose_name="Цена подписки в рублях")

    # Эти поля нужны, чтобы не создавать product/price заново при каждой оплате
    stripe_product_id = models.CharField(max_length=255, blank=True)
    stripe_price_id = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name
