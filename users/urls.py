from django.urls import path

from .views import CreateTelegramLinkView, MeView, RequestCodeView, TelegramWebhookView, VerifyCodeView

urlpatterns = [
    path("request-code/", RequestCodeView.as_view(), name="request_code"),
    path("verify-code/", VerifyCodeView.as_view(), name="verify_code"),
    path("me/", MeView.as_view(), name="user_me"),
    path("telegram/link/", CreateTelegramLinkView.as_view(), name="telegram_link"),
    path("telegram/webhook/", TelegramWebhookView.as_view(), name="telegram_webhook"),
]
