from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

from .managers import UserManager


class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    telegram_chat_id = models.BigIntegerField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager

    def __str__(self):
        return self.email


class TelegramLinkToken(models.Model):
    """Токен для привязки Telegram к аккаунту"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tg_tokens")
    token = models.CharField(max_length=64, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.token}"
