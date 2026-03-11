import requests
import stripe
from django.conf import settings


def stripe_create_product(name, description):
    """Создаем продукт в Stripe"""

    url = "https://api.stripe.com/v1/products"
    headers = {
        "Authorization": f"Bearer {settings.STRIPE_SECRET_KEY}",
    }
    data = {
        "name": name,
        "description": description,
    }

    response = requests.post(url, headers=headers, data=data, timeout=15)
    response.raise_for_status()
    return response.json()


def stripe_create_price(product_id: str, amount_rub: str, currency: str = "rub") -> dict:
    """Создаем цену в Stripe"""

    url = "https://api.stripe.com/v1/prices"
    headers = {
        "Authorization": f"Bearer {settings.STRIPE_SECRET_KEY}",
    }
    data = {
        "unit_amount": amount_rub * 100,
        "currency": currency,
        "product": product_id,
    }

    response = requests.post(url, headers=headers, data=data, timeout=15)
    response.raise_for_status()
    return response.json()


def stripe_create_checkout_session(
    price_id: str, success_url: str, cancel_url: str, user_id: int, creator_id: int
) -> dict:
    """Создаем Stripe Checkout Session"""

    url = "https://api.stripe.com/v1/checkout/sessions"
    headers = {
        "Authorization": f"Bearer {settings.STRIPE_SECRET_KEY}",
    }
    data = {
        "mode": "payment",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": 1,
        "metadata[user_id]": str(user_id),
        "metadata[creator_id]": str(creator_id),
    }

    response = requests.post(url, headers=headers, data=data, timeout=15)
    response.raise_for_status()
    return response.json()


def stripe_construct_event(payload, signature):
    return stripe.Webhook.construct_event(
        payload=payload,
        sig_header=signature,
        secret=settings.STRIPE_WEBHOOK_SECRET,
    )
