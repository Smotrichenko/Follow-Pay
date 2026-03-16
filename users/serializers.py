from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import PhoneLoginCode
from users.services import generate_login_code, send_code_to_console, send_telegram_message

User = get_user_model()


class RequestCodeSerializer(serializers.Serializer):
    """Сериализатор для запроса кода"""

    phone = serializers.CharField(max_length=20)

    def validate_phone(self, value):
        return value.strip()

    def save(self, **kwargs):
        phone = self.validated_data["phone"]

        code = generate_login_code()

        PhoneLoginCode.objects.create(
            phone=phone,
            code=code,
            is_used=False,
        )

        user = User.objects.filter(phone=phone).first()
        if user and user.telegram_chat_id:
            send_telegram_message(chat_id=str(user.telegram_chat_id), text=f"Ваш код для входа в аккаунт: {code}")
            delivery_method = "telegram"
        else:
            send_code_to_console(phone=phone, code=code)
            delivery_method = "console"

        return {
            "phone": phone,
            "delivery_method": delivery_method,
        }


class VerifyCodeSerializer(serializers.Serializer):
    """Сериализатор для проверки кода"""

    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        phone = attrs["phone"].strip()
        code = attrs["code"].strip()

        code_obj = (
            PhoneLoginCode.objects.filter(
                phone=phone,
                code=code,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if not code_obj:
            raise serializers.ValidationError("Неверный код или номер телефона.")

        if code_obj.created_data < timezone.now() - timedelta(minutes=10):
            raise serializers.ValidationError("Срок действия кода истёк.")

        attrs["phone"] = phone
        attrs["code"] = code

        return attrs

    def save(self, **kwargs):
        phone = self.validated_data["phone"]
        code_obj = self.validated_data["code_obj"]

        code_obj.is_used = True
        code_obj.save(update_fields=["is_used"])

        user, _ = User.objects.get_or_create(phone=phone)

        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class MeSerializer(serializers.ModelSerializer):
    """Отображение информации о текущем пользователе"""

    class Meta:
        model = User
        fields = ("id", "phone", "email", "telegram_chat_id")
        read_only_fields = ("id", "telegram_chat_id")
