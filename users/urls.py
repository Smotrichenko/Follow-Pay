from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import MeView, PasswordResetConfirmView, PasswordResetView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("token/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("me/", MeView.as_view()),

    path("password/reset/", PasswordResetView.as_view()),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view()),
]
