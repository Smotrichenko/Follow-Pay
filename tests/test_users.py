import pytest
from django.contrib.auth import get_user_model
from users.models import PhoneLoginCode

User = get_user_model()


@pytest.mark.django_db
def test_request_code_creates_code(api_client):
    response = api_client.post(
        "/api/users/request-code/",
        {"phone": "+79991112233"},
        format="json",
    )

    assert response.status_code == 200
    assert PhoneLoginCode.objects.filter(phone="+79991112233").count() == 1


@pytest.mark.django_db
def test_verify_code_creates_user_and_returns_tokens(api_client):
    PhoneLoginCode.objects.create(
        phone="+79991112233",
        code="1234",
        is_used=False,
    )

    response = api_client.post(
        "/api/users/verify-code/",
        {"phone": "+79991112233", "code": "1234"},
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data
    assert User.objects.filter(phone="+79991112233").exists()

    code_obj = PhoneLoginCode.objects.get(phone="+79991112233", code="1234")
    assert code_obj.is_used is True


@pytest.mark.django_db
def test_verify_code_with_invalid_code_returns_400(api_client):
    PhoneLoginCode.objects.create(
        phone="+79991112233",
        code="1234",
        is_used=False,
    )

    response = api_client.post(
        "/api/users/verify-code/",
        {"phone": "+79991112233", "code": "9999"},
        format="json",
    )

    assert response.status_code == 400
    assert User.objects.filter(phone="+79991112233").count() == 0


@pytest.mark.django_db
def test_me_endpoint_requires_auth(api_client):
    response = api_client.get("/api/users/me/")
    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_me_endpoint_returns_user_data(auth_client, user):
    response = auth_client.get("/api/users/me/")
    assert response.status_code == 200
    assert response.data["phone"] == user.phone
