import pytest
from unittest.mock import patch
from posts.models import Post


@pytest.mark.django_db
def test_create_post_requires_creator_profile(auth_client):
    response = auth_client.post(
        "/api/posts/create/",
        {
            "title": "My post",
            "body": "Text",
            "is_paid": False,
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_post_success(auth_client, creator):
    response = auth_client.post(
        "/api/posts/create/",
        {
            "title": "My post",
            "body": "Text",
            "is_paid": True,
        },
        format="json",
    )

    assert response.status_code == 201
    assert Post.objects.filter(title="My post", creator=creator).exists()


@pytest.mark.django_db
def test_free_post_is_visible_to_anyone(api_client, free_post):
    response = api_client.get(f"/api/posts/{free_post.id}/")
    assert response.status_code == 200
    assert response.data["title"] == free_post.title


@pytest.mark.django_db
def test_paid_post_denied_for_anonymous(api_client, paid_post):
    response = api_client.get(f"/api/posts/{paid_post.id}/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_paid_post_denied_without_subscription(api_client, paid_post, second_user):
    api_client.force_authenticate(user=second_user)

    response = api_client.get(f"/api/posts/{paid_post.id}/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_paid_post_allowed_for_subscriber(api_client, paid_post, second_user, subscription):
    api_client.force_authenticate(user=second_user)

    response = api_client.get(f"/api/posts/{paid_post.id}/")
    assert response.status_code == 200
    assert response.data["title"] == paid_post.title


@pytest.mark.django_db
@patch("posts.views.notify_subscribers_about_new_post.delay")
def test_publish_post(mock_notify, auth_client, creator):
    post = Post.objects.create(
        creator=creator,
        title="Draft",
        body="Draft body",
        is_paid=True,
        is_published=False,
    )

    response = auth_client.post(f"/api/posts/{post.id}/publish/")

    assert response.status_code == 200

    post.refresh_from_db()
    assert post.is_published is True
    assert post.published_at is not None
    mock_notify.assert_called_once_with(post.id)