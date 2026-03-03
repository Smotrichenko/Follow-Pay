from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers

User = get_user_model()


class PasswordResetSerializer(serializers.Serializer):
    """Инициализация сброса пароля"""

    email = serializers.EmailField()

    def save(self, **kwargs):
        email = self.validated_data["email"]
        user = User.objects.filter(email=email).first()
        if not user:
            return

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_link = f"http://localhost:8000/reset-password?uid={uid}&token={token}"

        send_mail(
            subject="Follow&Pay: сброс пароля",
            message=f"Чтобы сбросить пароль пройдите по ссылке:\n{reset_link}",
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "smotrichenko@yandex.ru"),
            recipient_list=[email],
            fail_silently=False,
        )


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Подтверждение сброса пароля"""

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def save(self):
        uid = self.validated_data["uid"]
        token = self.validated_data["token"]
        new_password = self.validated_data["new_password"]

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
        except Exception:
            raise serializers.ValidationError("Invalid uid")

        user = User.objects.filter(pk=user_id).first()
        if not user:
            raise serializers.ValidationError("Invalid user")

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError("Invalid token")

        user.set_password(new_password)
        user.save(update_fields=["password"])
