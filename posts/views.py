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
        return (
            Post.objects.filter(is_published=True).select_related("creator").order_by("-published_at", "-created_at")
        )


class MyPostListView(generics.ListAPIView):
    """Список постов текущего автора. Нужен для личного кабинета автора:
    он видит все свои посты, даже неопубликованные."""

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        creator = Creator.objects.filter(user=self.request.user).first()
        if not creator:
            return Post.objects.none()

        return Post.objects.filter(creator=creator).select_related("creator").order_by("-created_at")


class PostCreateView(generics.CreateAPIView):
    """Создание поста автором"""

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        creator = Creator.objects.filter(user=self.request.user).first()
        if not creator:
            raise ValueError("Сначало создайте профиль автора.")

        serializer.save(creator=creator)


class PostDetailView(generics.RetrieveAPIView):
    """Детали поста. Если пост платный - доступ только подписчикам автора"""

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.select_related("creator").filter(is_published=True)

    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()

        # Если пост бесплатный — всё ок
        if not post.is_paid:
            return super().retrieve(request, *args, **kwargs)

        # Если пользователь не залогинен — доступ запрещаем
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Для просмотра платного поста нужна авторизация."},
                status=401,
            )

        # Проверяем активную подписку на автора
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
            return Response({"detail": "Пост не найден."}, status=404)

        # Проверяем, что текущий пользователь — владелец поста
        if post.creator.user_id != request.user.id:
            return Response({"detail": "У вас нет доступа к этому посту."}, status=403)

        post.is_published = True
        post.published_at = timezone.now()
        post.save(update_fields=["is_published", "published_at"])

        # Уведомляем подписчиков только после публикации
        notify_subscribers_about_new_post.delay(post.id)

        return Response({"detail": "Пост опубликован."})


class PostUpdateView(generics.UpdateAPIView):
    """Редактирование поста"""

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsCreatorOwner]
    queryset = Post.objects.select_related("creator")

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj


class PostDeleteView(generics.DestroyAPIView):
    """Удаление поста. Удалять может только владелец поста."""

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsCreatorOwner]
    queryset = Post.objects.select_related("creator")

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj
