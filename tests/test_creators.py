import pytest
from unittest.mock import patch
from creators.models import Creator


@pytest.mark.django_db
@patch("creators.views.create_or_update_creator_stripe_data")
def test_create_creator_profile(mock_sync, auth_client, user):
    response = auth_client.post(
        "/api/creators/me/",
        {
            "display_name": "Creator One",
            "subscription_price_rub": 700,
        },
        format="json",
    )

    assert response.status_code == 201
    assert Creator.objects.filter(user=user).exists()

    creator = Creator.objects.get(user=user)
    assert creator.display_name == "Creator One"
    assert creator.subscription_price_rub == 700
    mock_sync.assert_called_once()


@pytest.mark.django_db
@patch("creators.views.create_or_update_creator_stripe_data")
def test_update_creator_profile(mock_sync, auth_client, creator):
    response = auth_client.post(
        "/api/creators/me/",
        {
            "display_name": "Updated Creator",
            "subscription_price_rub": 900,
        },
        format="json",
    )

    assert response.status_code == 200

    creator.refresh_from_db()
    assert creator.display_name == "Updated Creator"
    assert creator.subscription_price_rub == 900
    mock_sync.assert_called_once()


@pytest.mark.django_db
def test_creator_list_is_public(api_client, creator):
    response = api_client.get("/api/creators/")
    assert response.status_code == 200
    assert len(response.data) >= 1