import random
from datetime import datetime

import pytest

from products.models import Product, Tshirt, ShoppingCart, CartItem

from tests import product, tshirt_product, shopping_cart


class TestProduct:
    @pytest.mark.django_db
    def test_is_deleted_default_value(self):
        product = Product.objects.create(
            product_type=random.choice(Product.PRODUCT_TYPES),
            main_color="red",
            secondary_colors="blue",
            brand="Acme",
            inclusion_date=datetime.utcnow().date(),
            photo_url="https://example.com/product.png",
            unit_price=10.0,
            initial_stock=100,
            current_stock=80
        )

        assert product.is_deleted is False

    @pytest.mark.django_db
    def test_product_description(self, product: Product):
        descripcion = f"{product.main_color} {product.brand} {product.get_product_type_display()} with secondary " \
                      f"colors {product.secondary_colors}, included in the catalog in the year " \
                      f"{product.inclusion_date.year}"
        assert product.descripcion == descripcion

    @pytest.mark.django_db
    def test_thisrt_description(self, tshirt_product: Tshirt):
        descripcion = f"{tshirt_product.product_ptr.descripcion}, size {tshirt_product.size}, composition " \
                      f"{tshirt_product.composition_display}"
        assert tshirt_product.descripcion == descripcion

    @pytest.mark.django_db
    def test_composition_display(self, tshirt_product: Tshirt):
        composition_display = ", ".join([f"{m}: {p}%" for m, p in tshirt_product.composition.items()])
        assert tshirt_product.composition_display == composition_display


class TestShoppingCart:
    @pytest.mark.django_db
    def test_purchased_default_value(self):
        shopping_cart = ShoppingCart.objects.create()

        assert shopping_cart.purchased is False

    @pytest.mark.django_db
    def test_created_on_auto_now_add(self):
        utcnow = datetime.utcnow().date()
        shopping_cart = ShoppingCart.objects.create()

        assert shopping_cart.created_on >= utcnow


class TestCartItem:
    @pytest.mark.django_db
    def test_quantity_default_value(self, product: Product, shopping_cart: ShoppingCart):
        cart_item = CartItem.objects.create(product=product, shopping_cart=shopping_cart)

        assert cart_item.quantity == 0
