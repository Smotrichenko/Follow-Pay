from django.urls import path

from .views import CreatorDetailView, CreatorListView, CreatorMeView

urlpatterns = [
    path("", CreatorListView.as_view(), name="creator_list"),
    path("<int:pk>/", CreatorDetailView.as_view(), name="creator_detail"),
    path("me/", CreatorMeView.as_view(), name="creator_me"),
]
