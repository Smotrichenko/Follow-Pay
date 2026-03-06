from django.db import models
from django.conf import settings


class Creator(models.Model):
    """Автор - пользователь, который может публиковать посты и иметь подписчиков"""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=150)

    subscription_price_rub = models.PositiveIntegerField(default=500)
    subscription_currency = models.CharField(max_length=5, default="RUB")

    def __str__(self):
        return self.display_name
