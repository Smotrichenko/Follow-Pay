from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from creators.models import Creator
from subscriptions.models import Subscription

from .models import Post
from .permissions import IsCreatorOwner
from .serializers import PostSerializer
from .tasks import notify_subscribers_about_new_post


class PostListView(generics.ListAPIView):
    """Показываем только опубликованные посты"""

    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Post.objects.filter(is_published=True).select_related("creator")


class PostCreateView(generics.CreateAPIView):
    """Создание поста автором"""

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        creator = Creator.objects.filter(user=self.request.user).first()
        if not creator:
            raise ValueError("Пользователем не является автором.")

        serializer.save(creator=creator)


class PostDetailView(generics.RetrieveAPIView):
    """Детали поста. Если пост платный - доступ только подписчикам автора"""

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.select_related("creator").filter(is_published=True)

    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()

        if post.is_paid:
            if not request.user.is_authenticated:
                return Response({"detail": "Требуется авторизация"}, status=401)

            has_sub = Subscription.objects.filter(
                user=request.user, creator=post.creator, status=Subscription.Status.ACTIVE
            ).exists()

            if not has_sub:
                return Response({"detail": "Нет подписки на автора."})

        return super().retrieve(request, *args, **kwargs)


class PublishPostView(APIView):
    """Публикация поста"""

    permission_classes = [permissions.IsAuthenticated, IsCreatorOwner]

    def post(self, request, post_id):
        post = Post.objects.select_related("creator").filter(id=post_id).first()
        if not post:
            return Response({"detail": "Пост не найден."})

        self.check_object_permissions(request, post)

        post.is_published = True
        post.published_at = timezone.now()
        post.save(update_fields=["is_published", "published_at"])

        notify_subscribers_about_new_post.delay(post.id)

        return Response({"detail": "Пост опубликован."})
