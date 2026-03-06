from django.urls import path
from .views import CreatorMeView, CreatorListView, CreatorDetailView


urlpatterns = [
    path("", CreatorListView.as_view()),
    path("<int:pk>/", CreatorDetailView.as_view()),
    path("me/", CreatorMeView.as_view()),
]