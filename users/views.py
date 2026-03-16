import secrets

from django.db.models.expressions import result
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TelegramLinkToken
from .serializers import MeSerializer, RequestCodeSerializer, VerifyCodeSerializer


class RequestCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RequestCodeSerializer
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if result["delivery_method"] == "telegram":
            detail = "Код отправлен в Telegram."
        else:
            detail = "Код отправлен. Проверьте консоль сервера."

        return Response({"detail": detail})


class VerifyCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyCodeSerializer
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            {
                "refresh": result["refresh"],
                "access": result["access"],
                "user": MeSerializer(result["user"]).data,
            }
        )


class MeView(generics.RetrieveAPIView):
    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class CreateTelegramLinkView(APIView):
    """Создаем ссылку для привязки в Telegram"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = secrets.token_hex(16)

        TelegramLinkToken.objects.create(
            user=request.user,
            token=token,
            is_used=False,
        )

        link = f"https://t.me/followandpay_bot?start={token}"
        return Response({"telegram_link": link})


class TelegramWebhookView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data

        message = data.get("message") or {}
        text = data.get("text") or {}
        chat = data.get("chat") or {}
        chat_id = chat.get("id")

        if not text or not chat_id:
            return Response({"ok": True})

        if text.startswith("/start "):
            token = text.replace("/start ", "").strip()
            token_obj = TelegramLinkToken.objects.filter(token=token, is_used=False).select_related("user").first()

            if not token_obj:
                return Response({"ok": True})

            user = token_obj.user
            user.telegram_chat_id = chat_id
            user.save(update_fields=["telegram_chat_id"])

            token_obj.is_used = True
            token_obj.save(update_fields=["is_used"])

        return Response({"ok": True})
