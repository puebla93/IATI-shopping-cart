import random
from decimal import Decimal
from datetime import datetime

import pytest

from products.models import Cap, Tshirt, Product, ShoppingCart, CartItem

from products.serializers import (
    CapSerializer, TshirtSerializer, ProductListCreateSerializer, ProductRetrieveUpdateDestroySerializer,
    ProductInCartSerializer, CartItemSerializer, OrderSerializer
)

from tests import product, cap_product, tshirt_product, shopping_cart, cart_item


class TestCapSerializer:
    @pytest.mark.django_db
    def test_expected_fields(self, cap_product: Cap):
        serializer = CapSerializer(cap_product)

        expected_fields = ("logo_color", )

        assert serializer.data.keys() == set(expected_fields)
        assert serializer.data["logo_color"] == cap_product.logo_color

    @pytest.mark.django_db
    def test_required_fields(self):
        data = {
            "product_type": Product.CAP,
            "main_color": "red",
            "secondary_colors": "blue, green",
            "brand": "Acme",
            "inclusion_date": datetime.utcnow().date(),
            "photo_url": "https://example.com/cap.png",
            "unit_price": Decimal(10.0),
            "initial_stock": 100,
            "current_stock": 80
        }

        serializer = CapSerializer(data=data)

        assert not serializer.is_valid()
        assert "logo_color" in serializer.errors
        assert serializer.errors["logo_color"][0] == "This field is required."


class TestTshirtSerializer:
    @pytest.mark.django_db
    def test_expected_fields(self, tshirt_product: Tshirt):
        serializer = TshirtSerializer(tshirt_product)

        expected_fields = ["size", "composition", "gender", "has_sleeves", "description"]

        assert serializer.data.keys() == set(expected_fields)
        assert serializer.data["size"] == tshirt_product.size
        assert serializer.data["composition"] == tshirt_product.composition
        assert serializer.data["gender"] == tshirt_product.gender
        assert serializer.data["has_sleeves"] == tshirt_product.has_sleeves
        assert serializer.data["description"] == tshirt_product.description

    @pytest.mark.django_db
    def test_required_fields(self):
        removed_field = random.choice(["size", "composition", "gender", "has_sleeves"])

        data = {
            "product_type": Product.TSHIRT,
            "main_color": "red",
            "secondary_colors": "blue, green",
            "brand": "Acme",
            "inclusion_date": datetime.utcnow().date(),
            "photo_url": "https://example.com/tshirt.png",
            "unit_price": Decimal(10.0),
            "initial_stock": 100,
            "current_stock": 80,
            "size": "L",
            "composition": {"cotton": 50, "polyester": 50},
            "gender": "Man",
            "has_sleeves": True
        }
        data.pop(removed_field)

        serializer = TshirtSerializer(data=data)

        assert not serializer.is_valid()
        assert removed_field in serializer.errors
        assert serializer.errors[removed_field][0] == "This field is required."

    @pytest.mark.django_db
    def test_invalid_gender(self):
        data = {
            "gender": "dummy"
        }

        serializer = TshirtSerializer(data=data, partial=True)

        assert not serializer.is_valid()
        assert "gender" in serializer.errors
        assert serializer.errors["gender"][0] == "Dummy is an invalid gender."


class TestProductListCreateSerializer:
    @pytest.mark.django_db
    def test_expected_fields(self, product: Product):
        serializer = ProductListCreateSerializer(product)

        expected_fields = [
            "id", "product_type", "current_stock", "description", "main_color", "secondary_colors", "brand",
            "inclusion_date", "photo_url", "unit_price"
        ]

        assert "is_deleted" not in serializer.data.keys()
        assert "deleted_at" not in serializer.data.keys()
        assert "initial_stock" not in serializer.data.keys()
        assert serializer.data.keys() == set(expected_fields)

    @pytest.mark.django_db
    def test_validate_product_type_invalid(self):
        data = {
            "product_type": "dummy"
        }

        serializer = ProductListCreateSerializer(data=data, partial=True)

        assert not serializer.is_valid()
        assert "product_type" in serializer.errors
        assert serializer.errors["product_type"][0] == "Dummy is an invalid product type."

    @pytest.mark.django_db
    def test_validate_product_type_cannot_be_modified(self, product: Product):
        product_types = Product.PRODUCT_TYPES.copy()
        product_types.remove(product.product_type)
        new_product_type = random.choice(product_types)
        data = {
            "product_type": new_product_type
        }

        serializer = ProductListCreateSerializer(instance=product, data=data, partial=True)

        assert not serializer.is_valid()
        assert "product_type" in serializer.errors
        assert serializer.errors["product_type"][0] == "Product type cannot be modified."

    @pytest.mark.django_db
    def test_validate_initial_stock(self):
        data = {
            "initial_stock": -1
        }

        serializer = ProductListCreateSerializer(data=data, partial=True)

        assert not serializer.is_valid()
        assert "initial_stock" in serializer.errors
        assert serializer.errors["initial_stock"][0] == "Initial stock cannot be negative."

    @pytest.mark.django_db
    def test_cap_representation(self, cap_product: Cap):
        serializer = ProductListCreateSerializer(cap_product)

        expected_fields = [
            "id", "product_type", "current_stock", "description", "main_color", "secondary_colors", "brand",
            "inclusion_date", "photo_url", "unit_price", "logo_color"
        ]

        assert serializer.to_representation(cap_product).keys() == set(expected_fields)

    @pytest.mark.django_db
    def test_tshirt_representation(self, tshirt_product: Tshirt):
        serializer = ProductListCreateSerializer(tshirt_product)

        expected_fields = [
            "id", "product_type", "current_stock", "description", "main_color", "secondary_colors", "brand",
            "inclusion_date", "photo_url", "unit_price", "size", "composition", "gender", "has_sleeves", "description"
        ]

        assert serializer.to_representation(tshirt_product).keys() == set(expected_fields)

    @pytest.mark.django_db
    def test_cap_creation(self):
        data = {
            "product_type": Product.CAP,
            "main_color": "red",
            "secondary_colors": "blue, green",
            "brand": "Acme",
            "inclusion_date": datetime.utcnow().date(),
            "photo_url": "https://example.com/cap.png",
            "unit_price": Decimal(10.0),
            "initial_stock": 100,
            "logo_color": "balck"
        }

        serializer = ProductListCreateSerializer(data=data)
        assert serializer.is_valid()

        product: Cap = serializer.create(serializer.validated_data)

        assert product.product_type == data["product_type"]
        assert product.main_color == data["main_color"]
        assert product.secondary_colors == data["secondary_colors"]
        assert product.brand == data["brand"]
        assert product.inclusion_date == data["inclusion_date"]
        assert product.photo_url == data["photo_url"]
        assert product.unit_price == data["unit_price"]
        assert product.initial_stock == data["initial_stock"]
        assert product.current_stock == data["initial_stock"]
        assert product.logo_color == data["logo_color"]

    @pytest.mark.django_db
    def test_tshirt_creation(self):
        data = {
            "product_type": Product.TSHIRT,
            "main_color": "red",
            "secondary_colors": "blue, green",
            "brand": "Acme",
            "inclusion_date": datetime.utcnow().date(),
            "photo_url": "https://example.com/tshirt.png",
            "unit_price": Decimal(10.0),
            "initial_stock": 100,
            "size": "L",
            "composition": {"cotton": 50, "polyester": 50},
            "gender": "Man",
            "has_sleeves": True
        }

        serializer = ProductListCreateSerializer(data=data)
        assert serializer.is_valid()

        product: Tshirt = serializer.create(serializer.validated_data)

        assert product.product_type == data["product_type"]
        assert product.main_color == data["main_color"]
        assert product.secondary_colors == data["secondary_colors"]
        assert product.brand == data["brand"]
        assert product.inclusion_date == data["inclusion_date"]
        assert product.photo_url == data["photo_url"]
        assert product.unit_price == data["unit_price"]
        assert product.initial_stock == data["initial_stock"]
        assert product.current_stock == data["initial_stock"]
        assert product.size == data["size"]
        assert product.composition == data["composition"]
        assert product.gender == data["gender"]
        assert product.has_sleeves == data["has_sleeves"]


class TestProductRetrieveUpdateDestroySerializer:
    @pytest.mark.django_db
    def test_expected_fields(self, product: Product):
        serializer = ProductRetrieveUpdateDestroySerializer(product)

        expected_fields = [
            "id", "product_type", "description", "main_color", "secondary_colors", "brand",
            "inclusion_date", "photo_url", "unit_price", "current_stock"
        ]

        assert "is_deleted" not in serializer.data.keys()
        assert "deleted_at" not in serializer.data.keys()
        assert "initial_stock" not in serializer.data.keys()
        assert serializer.data.keys() == set(expected_fields)

    @pytest.mark.django_db
    def test_cap_representation(self, cap_product: Cap):
        serializer = ProductRetrieveUpdateDestroySerializer(cap_product)

        expected_fields = [
            "id", "product_type", "current_stock", "description", "main_color", "secondary_colors", "brand",
            "inclusion_date", "photo_url", "unit_price", "logo_color"
        ]

        assert serializer.to_representation(cap_product).keys() == set(expected_fields)

    @pytest.mark.django_db
    def test_tshirt_representation(self, tshirt_product: Tshirt):
        serializer = ProductRetrieveUpdateDestroySerializer(tshirt_product)

        expected_fields = [
            "id", "product_type", "current_stock", "description", "main_color", "secondary_colors", "brand",
            "inclusion_date", "photo_url", "unit_price", "size", "composition", "gender", "has_sleeves", "description"
        ]

        assert serializer.to_representation(tshirt_product).keys() == set(expected_fields)

    @pytest.mark.django_db
    def test_cap_update(self, cap_product: Cap):
        data = {
            "main_color": "white",
            "secondary_colors": "gray, black",
            "brand": "Acme",
            "inclusion_date": datetime.utcnow().date(),
            "photo_url": "https://example.com/cap1.png",
            "unit_price": 15.0,
            "current_stock": 50,
            "logo_color": "yellow"
        }

        serializer = ProductRetrieveUpdateDestroySerializer(data=data)
        assert serializer.is_valid()

        product: Cap = serializer.update(cap_product, serializer.validated_data)

        assert product.main_color == data["main_color"]
        assert product.secondary_colors == data["secondary_colors"]
        assert product.brand == data["brand"]
        assert product.inclusion_date == data["inclusion_date"]
        assert product.photo_url == data["photo_url"]
        assert product.unit_price == data["unit_price"]
        assert product.current_stock == data["current_stock"]
        assert product.logo_color == data["logo_color"]

    @pytest.mark.django_db
    def test_tshirt_type_update(self, tshirt_product: Tshirt):
        data = {
            "main_color": "white",
            "secondary_colors": "gray, black",
            "brand": "Acme",
            "inclusion_date": datetime.utcnow().date(),
            "photo_url": "https://example.com/tshirt1.png",
            "unit_price": 15.0,
            "current_stock": 50,
            "size": "S",
            "composition": {"nylon": 30, "wool": 40, "silk": 30},
            "gender": "Unisex",
            "has_sleeves": False
        }

        serializer = ProductRetrieveUpdateDestroySerializer(data=data)
        assert serializer.is_valid()

        product: Tshirt = serializer.update(tshirt_product, serializer.validated_data)

        assert product.main_color == data["main_color"]
        assert product.secondary_colors == data["secondary_colors"]
        assert product.brand == data["brand"]
        assert product.inclusion_date == data["inclusion_date"]
        assert product.photo_url == data["photo_url"]
        assert product.unit_price == data["unit_price"]
        assert product.current_stock == data["current_stock"]
        assert product.size == data["size"]
        assert product.composition == data["composition"]
        assert product.gender == data["gender"]
        assert product.has_sleeves == data["has_sleeves"]


class TestProductInCartSerializer:
    @pytest.mark.django_db
    def test_expected_fields(self, product: Product):
        serializer = ProductInCartSerializer(product)

        expected_fields = ["product_id", "description", "photo_url", "unit_price"]

        assert serializer.data.keys() == set(expected_fields)
        assert serializer.data["product_id"] == product.id
        assert serializer.data["description"] == product.description
        assert serializer.data["photo_url"] == product.photo_url
        assert Decimal(serializer.data["unit_price"]) == product.unit_price

    @pytest.mark.django_db
    def test_required_fields(self):
        removed_field = random.choice(["product_id", "description", "photo_url", "unit_price"])

        data = {
            "product_id": random.randint(1, 100),
            "description": "fake description",
            "photo_url": "https://example.com/product.png",
            "unit_price": Decimal(10.0)
        }
        data.pop(removed_field)

        serializer = ProductInCartSerializer(data=data)

        assert not serializer.is_valid()
        assert removed_field in serializer.errors
        assert serializer.errors[removed_field][0] == "This field is required."


class TestCartItemSerializer:
    @pytest.mark.django_db
    def test_quantity_default_value(self, product: Product):
        data = {
            "product_id": 1
        }

        serializer = CartItemSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["quantity"] == 1

    @pytest.mark.django_db
    def test_validate_product_id_invalid(self):
        data = {
            "product_id": 1
        }

        serializer = CartItemSerializer(data=data)

        assert not serializer.is_valid()
        assert "product_id" in serializer.errors
        assert serializer.errors["product_id"][0] == "Product with id 1 does not exist."

    @pytest.mark.django_db
    def test_validate_quantity_is_zero(self, product: Product):
        data = {
            "product_id": 1,
            "quantity": 0
        }

        serializer = CartItemSerializer(data=data)

        assert not serializer.is_valid()
        assert "quantity" in serializer.errors
        assert serializer.errors["quantity"][0] == "You need to add or remove products from your shopping cart, " \
                                                   "cannot be zero."

    @pytest.mark.django_db
    def test_validate_quantity_not_enough_stock_available(self, product: Product):
        data = {
            "product_id": 1,
            "quantity": product.current_stock + 1
        }

        serializer = CartItemSerializer(data=data)

        assert not serializer.is_valid()
        assert "quantity" in serializer.errors
        assert serializer.errors["quantity"][0] == "Not enough stock available."

    @pytest.mark.django_db
    def test_to_representation(self, cart_item: CartItem):
        serializer = CartItemSerializer(cart_item)

        expected_fields = ["product_id", "description", "photo_url", "unit_price", "quantity"]

        assert serializer.to_representation(cart_item).keys() == set(expected_fields)

    @pytest.mark.django_db
    def test_cart_item_creation_no_existing_shopping_cart(self, product: Product):
        data = {
            "product_id": 1,
            "quantity": random.randint(1, product.current_stock)
        }

        serializer = CartItemSerializer(data=data)

        assert serializer.is_valid()

        cart_item: CartItem = serializer.create(serializer.validated_data)

        assert cart_item.product == product
        assert cart_item.shopping_cart is not None
        assert cart_item.quantity == data["quantity"]

    @pytest.mark.django_db
    def test_cart_item_creation_existing_shopping_cart(self, product: Product, shopping_cart: ShoppingCart):
        data = {
            "product_id": 1,
            "quantity": random.randint(1, product.current_stock)
        }

        serializer = CartItemSerializer(data=data)

        assert serializer.is_valid()

        cart_item: CartItem = serializer.create(serializer.validated_data)

        assert cart_item.product == product
        assert cart_item.shopping_cart == shopping_cart
        assert cart_item.quantity == data["quantity"]

    @pytest.mark.django_db
    def test_cart_item_creation_new_cart_item(self, product: Product, shopping_cart: ShoppingCart):
        data = {
            "product_id": 1,
            "quantity": random.randint(1, product.current_stock)
        }

        serializer = CartItemSerializer(data=data)

        assert serializer.is_valid()

        cart_item: CartItem = serializer.create(serializer.validated_data)

        assert cart_item.product == product
        assert cart_item.shopping_cart == shopping_cart
        assert cart_item.quantity == data["quantity"]

    @pytest.mark.django_db
    def test_cart_item_creation_add_to_cart_item(self, cart_item: CartItem):
        data = {
            "product_id": 1,
            "quantity": random.randint(1, cart_item.product.current_stock - cart_item.quantity)
        }

        serializer = CartItemSerializer(data=data)

        assert serializer.is_valid()

        serializer.create(serializer.validated_data)

        current_quantity = cart_item.quantity
        current_stock = cart_item.product.current_stock
        cart_item.refresh_from_db()

        assert cart_item.quantity == current_quantity + data["quantity"]
        assert cart_item.product.current_stock == current_stock - data["quantity"]

    @pytest.mark.django_db
    def test_cart_item_creation_remove_from_cart_item(self, cart_item: CartItem):
        data = {
            "product_id": 1,
            "quantity": random.randint(1, cart_item.quantity) * -1
        }

        serializer = CartItemSerializer(data=data)

        assert serializer.is_valid()

        serializer.create(serializer.validated_data)

        current_quantity = cart_item.quantity
        cart_item.refresh_from_db()

        assert cart_item.quantity == data["quantity"] + current_quantity


class TestOrderSerializer:
    @pytest.mark.django_db
    def test_required_fields(self):
        removed_field = random.choice(["name", "last_name", "address", "email", "mobile_number"])

        data = {
            "name": "Jane",
            "last_name": "Doe",
            "address": "Barcelona, CP 08001",
            "email": "jane.doe@gmail.com",
            "mobile_number": "+34123456789"
        }
        data.pop(removed_field)

        serializer = OrderSerializer(data=data)

        assert not serializer.is_valid()
        assert removed_field in serializer.errors
        assert serializer.errors[removed_field][0] == "This field is required."
