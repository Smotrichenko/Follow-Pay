from django.urls import path
from .views import MySubscriptionsView, UnsubscribeView, SubscriptionStatusView

urlpatterns = [
    path("mine/", MySubscriptionsView.as_view()),
    path("<int:creator_id>/unsubscribe/", UnsubscribeView.as_view()),
    path("<int:creator_id>/status/", SubscriptionStatusView.as_view()),
]