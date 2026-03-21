from django.conf import settings
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from creators.models import Creator
from payments.services import stripe_construct_event, stripe_create_checkout_session
from subscriptions.models import Subscription
from users.tasks import send_telegram_message_task

from .models import Payment


class CreateCheckoutSessionView(APIView):
    """Создание Stripe Checkout Session для подписки на автора"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        creator_id = request.data.get("creator_id")
        if not creator_id:
            return Response({"detail": "creator_id is required"}, status=400)

        creator = Creator.objects.filter(id=creator_id).first()
        if not creator:
            return Response({"detail": "Автор не найден."}, status=404)

        if not creator.stripe_price_id:
            return Response({"detail": "У автора не настроена цена."}, status=400)

        success_url = getattr(settings, "STRIPE_SUCCESS_URL")
        cancel_url = getattr(settings, "STRIPE_CANCEL_URL")

        session = stripe_create_checkout_session(
            price_id=creator.stripe_price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            user_id=request.user.id,
            creator_id=creator.id,
        )

        Payment.objects.create(
            user=request.user, creator=creator, stripe_session_id=session["id"], status=Payment.Status.PENDING
        )

        return Response({"checkout_url": session["url"]})


class StripeWebhookView(APIView):
    """Webhook от Stripe"""
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        signature = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe_construct_event(payload=payload, signature=signature)
        except Exception as e:
            print("STRIPE WEBHOOK ERROR:", str(e))
            return Response({"detail": "Invalid Webhook"}, status=400)

        print("STRIPE WEBHOOK HIT")
        print(event)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            session_id = session.get("id")
            metadata = session.get("metadata", {})

            user_id = int(metadata.get("user_id", 0))
            creator_id = int(metadata.get("creator_id", 0))

            payment = Payment.objects.filter(stripe_session_id=session_id).first()

            if payment and payment.status != Payment.Status.PAID:
                payment.status = Payment.Status.PAID
                payment.save(update_fields=["status"])

                Subscription.objects.update_or_create(
                    user_id=user_id, creator_id=creator_id, defaults={"status": Subscription.Status.ACTIVE}
                )

                send_telegram_message_task.delay(
                    user_id=user_id, text="✅ Оплата прошла успешно! Подписка активирована."
                )
        return Response({"ok": True})


class SuccessView(APIView):
    """Временный endpoint после успешной оплаты."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "Оплата прошла успешно."})


class CancelView(APIView):
    """Временный endpoint, если пользователь отменил оплату."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "Оплата отменена."})
