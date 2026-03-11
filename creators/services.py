from payments.services import stripe_create_product, stripe_create_price


def create_or_update_creator_stripe_data(creator):
    """Синхронизация автора со Stripe"""

    # Если продукт еще не создан - создаем
    if not creator.stripe_product_id:
        product = stripe_create_product(
            name=f"Подписка на автора {creator.display_name}",
            description=f"Подписка на контент автора {creator.display_name}",
        )
        creator.stripe_product_id = product["id"]

    # Создаем новую цену на основе текущей цены в рублях
    price = stripe_create_price(
        product_id=creator.stripe_product_id, amount_rub=creator.subscription_price_rub, currency="rub"
    )

    creator.stripe_price_id = price["id"]

    creator.save(update_fields=["stripe_product_id", "stripe_price_id"])
