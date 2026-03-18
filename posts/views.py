from django.utils import timezone

from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from creators.models import Creator
from subscriptions.models import Subscription

from .models import Post
from .serializers import PostSerializer
from .permissions import IsCreatorOwner
from .tasks import notify_subscribers_about_new_post


class PostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True
        ).select_related("creator").order_by("-published_at", "-created_at")


class MyPostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        creator = Creator.objects.filter(user=self.request.user).first()
        if not creator:
            return Post.objects.none()

        return Post.objects.filter(
            creator=creator
        ).select_related("creator").order_by("-created_at")


class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        creator = Creator.objects.filter(user=self.request.user).first()
        if not creator:
            raise ValidationError("Сначала создайте профиль автора.")

        serializer.save(creator=creator)


class PostDetailView(generics.RetrieveAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Post.objects.select_related("creator").filter(is_published=True)

    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()

        # Бесплатный пост доступен всем
        if not post.is_paid:
            return super().retrieve(request, *args, **kwargs)

        # Для платного нужна авторизация
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Для просмотра платного поста нужна авторизация."},
                status=401,
            )

        # Автор видит свой пост всегда
        if post.creator.user_id == request.user.id:
            return super().retrieve(request, *args, **kwargs)

        # Проверяем активную подписку
        has_subscription = Subscription.objects.filter(
            user=request.user,
            creator=post.creator,
            status=Subscription.Status.ACTIVE,
        ).exists()

        if not has_subscription:
            return Response(
                {"detail": "У вас нет активной подписки на этого автора."},
                status=403,
            )

        return super().retrieve(request, *args, **kwargs)


class PostUpdateView(generics.UpdateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsCreatorOwner]
    queryset = Post.objects.select_related("creator")

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj


class PostDeleteView(generics.DestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsCreatorOwner]
    queryset = Post.objects.select_related("creator")

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj


class PublishPostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id: int):
        post = Post.objects.select_related("creator").filter(id=post_id).first()
        if not post:
            return Response({"detail": "Пост не найден."}, status=404)

        if post.creator.user_id != request.user.id:
            return Response({"detail": "У вас нет доступа к этому посту."}, status=403)

        post.is_published = True
        post.published_at = timezone.now()
        post.save(update_fields=["is_published", "published_at"])

        notify_subscribers_about_new_post.delay(post.id)

        return Response({"detail": "Пост опубликован."})
