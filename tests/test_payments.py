import pytest
from unittest.mock import patch
from payments.models import Payment
from subscriptions.models import Subscription


@pytest.mark.django_db
def test_create_checkout_session_requires_auth(api_client, creator):
    response = api_client.post(
        "/api/payments/checkout-session/",
        {"creator_id": creator.id},
        format="json",
    )
    assert response.status_code in (401, 403)


@pytest.mark.django_db
@patch("payments.views.stripe_create_checkout_session")
def test_create_checkout_session_success(mock_checkout, auth_client, user, creator):
    mock_checkout.return_value = {
        "id": "cs_test_123",
        "url": "https://checkout.stripe.com/test",
    }

    response = auth_client.post(
        "/api/payments/checkout-session/",
        {"creator_id": creator.id},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["checkout_url"] == "https://checkout.stripe.com/test"
    assert Payment.objects.filter(
        user=user,
        creator=creator,
        stripe_session_id="cs_test_123",
    ).exists()


@pytest.mark.django_db
@patch("payments.views.send_telegram_message_task.delay")
@patch("payments.views.stripe_construct_event")
def test_stripe_webhook_marks_payment_paid_and_creates_subscription(
    mock_construct_event,
    mock_send_telegram,
    api_client,
    second_user,
    creator,
):
    payment = Payment.objects.create(
        user=second_user,
        creator=creator,
        stripe_session_id="cs_test_123",
        status=Payment.Status.PENDING,
    )

    mock_construct_event.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "metadata": {
                    "user_id": str(second_user.id),
                    "creator_id": str(creator.id),
                },
            }
        },
    }

    response = api_client.post(
        "/api/payments/stripe/webhook/",
        data="{}",
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="test_signature",
    )

    assert response.status_code == 200

    payment.refresh_from_db()
    assert payment.status == Payment.Status.PAID

    assert Subscription.objects.filter(
        user=second_user,
        creator=creator,
        status=Subscription.Status.ACTIVE,
    ).exists()

    mock_send_telegram.assert_called_once()