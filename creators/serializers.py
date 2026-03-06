from rest_framework import serializers
from .models import Creator


class CreatorSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра автора"""

    class Meta:
        model = Creator
        fields = ("id", "display_name", "subscription_price_rub", "subscription_currency")
        read_only_fields = ("id",)


class CreatorMeUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления профиля автора и цены подписки"""

    class Meta:
        model = Creator
        fields = ("display_name", "subscription_price_rub")

    def validate_subscription_price_rub(self, value):
        if value < 100:
            raise serializers.ValidationError("Цена подписки не может быть ниже 100 рублей.")
        if value > 10000:
            raise serializers.ValidationError("Цена подписки не может быть более 10000 рублей.")
        return value
