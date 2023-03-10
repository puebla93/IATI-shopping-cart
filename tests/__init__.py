import random
from datetime import datetime
from decimal import Decimal

import pytest

from rest_framework.test import APIClient

from products.models import Product, Cap, Tshirt, ShoppingCart, CartItem


@pytest.fixture
def product() -> Product:
    return Product.objects.create(
        product_type=random.choice(Product.PRODUCT_TYPES),
        main_color="red",
        secondary_colors="blue, green",
        brand="Acme",
        inclusion_date=datetime.utcnow().date(),
        photo_url="https://example.com/product.png",
        unit_price=Decimal(10.0),
        initial_stock=100,
        current_stock=80
    )


@pytest.fixture
def cap_product() -> Cap:
    return Cap.objects.create(
        product_type=Product.CAP,
        main_color="red",
        secondary_colors="blue, green",
        brand="Acme",
        inclusion_date=datetime.utcnow().date(),
        photo_url="https://example.com/cap.png",
        unit_price=Decimal(10.0),
        initial_stock=100,
        current_stock=80,
        logo_color="black"
    )


@pytest.fixture
def tshirt_product() -> Tshirt:
    return Tshirt.objects.create(
        product_type=Product.TSHIRT,
        main_color="red",
        secondary_colors="blue, green",
        brand="Acme",
        inclusion_date=datetime.utcnow().date(),
        photo_url="https://example.com/tshirt.png",
        unit_price=Decimal(10.0),
        initial_stock=100,
        current_stock=80,
        size="L",
        composition={"cotton": 50, "polyester": 50},
        gender="Man",
        has_sleeves=True
    )


@pytest.fixture
def shopping_cart() -> ShoppingCart:
    return ShoppingCart.objects.create()


@pytest.fixture
def cart_item(product: Product, shopping_cart: ShoppingCart) -> CartItem:
    return CartItem.objects.create(shopping_cart=shopping_cart, product=product, quantity=5)


@pytest.fixture
def api_client():
    return APIClient()
