from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Creator
from .serializers import CreatorMeUpdateSerializer, CreatorSerializer
from .services import create_or_update_creator_stripe_data


class CreatorListView(generics.ListAPIView):
    queryset = Creator.objects.all().select_related("user").order_by("display_name")
    serializer_class = CreatorSerializer
    permission_classes = [permissions.AllowAny]


class CreatorDetailView(generics.RetrieveAPIView):
    queryset = Creator.objects.all().select_related("user")
    serializer_class = CreatorSerializer
    permission_classes = [permissions.AllowAny]


class CreatorMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        creator = Creator.objects.filter(user=request.user).first()
        if not creator:
            return Response({"detail": "Профиль автора еще не создан!"}, status=404)
        return Response(CreatorSerializer(creator).data)

    def post(self, request):
        creator = Creator.objects.filter(user=request.user).first()
        if creator:
            s = CreatorMeUpdateSerializer(creator, data=request.data, partial=True)
            s.is_valid(raise_exception=True)
            s.save()

            create_or_update_creator_stripe_data(creator)

            return Response(CreatorSerializer(creator).data)

        s = CreatorMeUpdateSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        creator = Creator.objects.create(
            user=request.user,
            display_name=s.validated_data["display_name"],
            subscription_price_rub=s.validated_data.get("subscription_price_rub", 500),
        )
        create_or_update_creator_stripe_data(creator)

        return Response(CreatorSerializer(creator).data, status=201)
