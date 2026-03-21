import pytest
from users.models import TelegramLinkToken


@pytest.mark.django_db
def test_create_telegram_link_returns_url(auth_client, user, settings):
    settings.TELEGRAM_BOT_NAME = "followandpay_bot"

    response = auth_client.post("/api/users/telegram/link/", {}, format="json")

    assert response.status_code == 200
    assert "telegram_link" in response.data
    assert "followandpay_bot" in response.data["telegram_link"]
    assert TelegramLinkToken.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_telegram_webhook_connects_user(api_client, user):
    token = TelegramLinkToken.objects.create(
        user=user,
        token="testtoken123",
        is_used=False,
    )

    payload = {
        "message": {
            "text": "/start testtoken123",
            "chat": {"id": 555123},
        }
    }

    response = api_client.post(
        "/api/users/telegram/webhook/",
        payload,
        format="json",
    )

    assert response.status_code == 200

    user.refresh_from_db()
    token.refresh_from_db()

    assert user.telegram_chat_id == 555123
    assert token.is_used is True
