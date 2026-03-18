import pytest
from creators.models import Creator
from subscriptions.models import Subscription


@pytest.mark.django_db
def test_my_subscriptions(auth_client, user, second_user):
    creator = Creator.objects.create(
        user=second_user,
        display_name="Author Two",
        subscription_price_rub=500,
        stripe_product_id="prod_test_2",
        stripe_price_id="price_test_2",
    )

    Subscription.objects.create(
        user=user,
        creator=creator,
        status=Subscription.Status.ACTIVE,
    )

    response = auth_client.get("/api/subscriptions/mine/")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["creator_display_name"] == creator.display_name


@pytest.mark.django_db
def test_subscription_status(auth_client, user, second_user):
    creator = Creator.objects.create(
        user=second_user,
        display_name="Author Two",
        subscription_price_rub=500,
        stripe_product_id="prod_test_2",
        stripe_price_id="price_test_2",
    )

    Subscription.objects.create(
        user=user,
        creator=creator,
        status=Subscription.Status.ACTIVE,
    )

    response = auth_client.get(f"/api/subscriptions/{creator.id}/status/")
    assert response.status_code == 200
    assert response.data["is_active"] is True
