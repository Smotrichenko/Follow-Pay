from django.urls import path

from .views import CreateTelegramLinkView, MeView, RequestCodeView, TelegramWebhookView, VerifyCodeView

urlpatterns = [
    path("request-code/", RequestCodeView.as_view(), name="request_code"),
    path("verify-code/", VerifyCodeView.as_view(), name="verify_code"),
    path("me/", MeView.as_view()),
    path("telegram/link/", CreateTelegramLinkView.as_view()),
    path("telegram/webhook/", TelegramWebhookView.as_view()),
]
