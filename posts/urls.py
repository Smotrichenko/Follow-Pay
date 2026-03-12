from django.urls import path

from .views import (MyPostListView, PostCreateView, PostDeleteView, PostDetailView, PostListView, PostUpdateView,
                    PublishPostView)

urlpatterns = [
    path("", PostListView.as_view(), name="post_list"),
    path("mine/", MyPostListView.as_view(), name="my_posts"),
    path("create/", PostCreateView.as_view(), name="post_create"),
    path("<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("<int:pk>/update/", PostUpdateView.as_view(), name="post_update"),
    path("<int:pk>/delete/", PostDeleteView.as_view(), name="post_delete"),
    path("<int:post_id>/publish/", PublishPostView.as_view(), name="post_publish"),
]