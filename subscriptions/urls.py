from django.urls import path

from .views import MySubscriptionsView, SubscriptionStatusView, UnsubscribeView


urlpatterns = [
    path("mine/", MySubscriptionsView.as_view(), name="my_subscriptions"),
    path("<int:creator_id>/unsubscribe/", UnsubscribeView.as_view(), name="unsubscribe"),
    path("<int:creator_id>/status/", SubscriptionStatusView.as_view(), name="subscription_status"),
]
