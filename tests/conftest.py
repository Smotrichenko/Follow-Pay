import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from creators.models import Creator
from posts.models import Post
from subscriptions.models import Subscription

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(phone="+79990000001", email="user1@test.com")


@pytest.fixture
def second_user():
    return User.objects.create_user(phone="+79990000002", email="user2@test.com")


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def creator(user):
    return Creator.objects.create(
        user=user,
        display_name="Test Creator",
        subscription_price_rub=500,
        stripe_product_id="prod_test",
        stripe_price_id="price_test",
    )


@pytest.fixture
def paid_post(creator):
    return Post.objects.create(
        creator=creator,
        title="Paid post",
        body="Secret paid content",
        is_paid=True,
        is_published=True,
    )


@pytest.fixture
def free_post(creator):
    return Post.objects.create(
        creator=creator,
        title="Free post",
        body="Public content",
        is_paid=False,
        is_published=True,
    )


@pytest.fixture
def subscription(second_user, creator):
    return Subscription.objects.create(
        user=second_user,
        creator=creator,
        status=Subscription.Status.ACTIVE,
    )
