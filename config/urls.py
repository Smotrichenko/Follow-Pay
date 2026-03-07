from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/auth/", include("users.urls")),
    path("api/creators/", include("creators.urls")),
    path("api/subscriptions/", include("subscriptions.urls")),


]
