from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from config import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("web.urls")),
    path("api/auth/", include("users.urls")),
    path("api/creators/", include("creators.urls")),
    path("api/subscriptions/", include("subscriptions.urls")),
    path("api/posts/", include("posts.urls")),
    path("api/payments/", include("payments.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)