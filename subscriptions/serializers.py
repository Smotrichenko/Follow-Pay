from rest_framework import serializers
from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    """Показ подписок пользователя"""

    creator_display_name = serializers.CharField(source="creator.display_name", read_only=True)

    model = Subscription
    fields = ("id", "creator", "creator_display_name", "status", "created_at")
    read_only_fields = ("id", "status", "created_at")


class SubscriberSerializer(serializers.Serializer):
    """Входные данные для подписки"""

    creator_id = serializers.IntegerField()
