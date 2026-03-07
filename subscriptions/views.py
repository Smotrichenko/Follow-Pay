from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.response import Response

from creators.models import Creator
from .serializers import SubscriberSerializer, SubscriptionSerializer
from .models import Subscription


class MySubscriptionsView(generics.ListAPIView):
    """Мои подписки"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).select_related("creator")


class UnsubscribeView(APIView):
    """Отписка от автора"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, creator_id):
        sub = Subscription.objects.filter(user=request.user, creator_id=creator_id).first()
        if not sub:
            return Response({"detail": "Подписка не найдена."}, status=404)

        sub.status = Subscription.Status.CANCELED
        sub.save(update_fields=["status"])
        return Response({"detail": "Вы отписались от автора."})


class SubscriptionStatusView(APIView):
    """Проверка, есть ли активная подписка на автора"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, creator_id):
        is_active = Subscription.objects.filter(user=request.user, creator_id=creator_id, status=Subscription.Status.ACTIVE).exists()
        return Response({"creator_id": creator_id, "is_active": is_active})
