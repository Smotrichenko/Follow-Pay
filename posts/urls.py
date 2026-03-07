from django.urls import path

from .views import PostCreateView, PostDetailView, PostListView, PublishPostView

urlpatterns = [
    path("", PostListView.as_view(), name="post_list"),
    path("create/", PostCreateView.as_view(), name="post_create"),
    path("<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("<int:post_id>/publish/", PublishPostView.as_view(), name="post_publish"),
]