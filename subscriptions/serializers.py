from rest_framework import serializers
from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    """Показ подписок пользователя"""

    creator_display_name = serializers.CharField(source="creator.display_name", read_only=True)
    creator_price_rub = serializers.IntegerField(source="creator.subscription_price_rub", read_only=True)

    class Meta:
        model = Subscription
        fields = (
            "id",
            "creator",
            "creator_display_name",
            "creator_price_rub",
            "status",
            "created_at",
        )
        read_only_fields = (
            "id",
            "creator_display_name",
            "creator_price_rub",
            "created_at",
        )
