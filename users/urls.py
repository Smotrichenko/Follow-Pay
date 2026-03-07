from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (CreateTelegramLinkView, MeView, PasswordResetConfirmView, PasswordResetView, RegisterView,
                    TelegramWebhookView)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("token/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("me/", MeView.as_view()),

    path("password/reset/", PasswordResetView.as_view()),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view()),

    path("telegram/link/", CreateTelegramLinkView.as_view()),
    path("telegram/webhook/", TelegramWebhookView.as_view()),
]
