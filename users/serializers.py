from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Регистрация пользователя"""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "password")

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
        )


class MeSerializer(serializers.ModelSerializer):
    """Отображение информации о текущем пользователе"""

    class Meta:
        model = User
        fields = ("id", "email", "telegram_chat_id")
        read_only_fields = ("id", "telegram_chat_id")
