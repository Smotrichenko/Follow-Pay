from django.urls import path

from .views import (
    HomeView,
    CreatorListView,
    CreatorDetailView,
    PostDetailView,

    login_view,
    logout_view,
    subscribe_creator_view,
    payment_success_view,
    payment_cancel_view,
    dashboard_view,
    my_subscriptions_view,
    my_posts_view,
    creator_form_view,
    post_create_view,
    post_update_view,
    post_publish_view, verify_code_view,
)

urlpatterns = [
    path("", HomeView.as_view(), name="web_home"),
    path("creators/", CreatorListView.as_view(), name="web_creators"),
    path("creators/<int:pk>/", CreatorDetailView.as_view(), name="web_creator_detail"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="web_post_detail"),

    path("login/", login_view, name="web_login"),
    path("verify-code/", verify_code_view, name="web_verify_code"),
    path("logout/", logout_view, name="web_logout"),

    path("subscribe/<int:creator_id>/", subscribe_creator_view, name="web_subscribe"),

    path("payment/success/", payment_success_view, name="web_payment_success"),
    path("payment/cancel/", payment_cancel_view, name="web_payment_cancel"),

    path("dashboard/", dashboard_view, name="web_dashboard"),
    path("dashboard/subscriptions/", my_subscriptions_view, name="web_my_subscriptions"),
    path("dashboard/posts/", my_posts_view, name="web_my_posts"),

    path("dashboard/creator/", creator_form_view, name="web_creator_form"),
    path("dashboard/posts/create/", post_create_view, name="web_post_create"),
    path("dashboard/posts/<int:post_id>/edit/", post_update_view, name="web_post_edit"),
    path("dashboard/posts/<int:post_id>/publish/", post_publish_view, name="web_post_publish"),
]
