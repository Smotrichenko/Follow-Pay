from django.urls import path

from .views import CancelView, CreateCheckoutSessionView, StripeWebhookView, SuccessView

urlpatterns = [
    path("checkout-session/", CreateCheckoutSessionView.as_view(), name="checkout_session"),
    path("stripe/webhook/", StripeWebhookView.as_view(), name="stripe_webhook"),
    path("success/", SuccessView.as_view(), name="payment_success"),
    path("cancel/", CancelView.as_view(), name="payment_cancel"),
]
