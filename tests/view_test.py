import json
import random
from datetime import datetime, timedelta

import pytest
from pytest_mock import MockerFixture

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from products.models import Product, Cap, Tshirt, ShoppingCart, CartItem

from tests import product, cap_product, tshirt_product, shopping_cart, cart_item, api_client


class TestProductListCreate:
    URL = "http://127.0.0.1:8000/api/v1/products/"

    CAP_PRODUCT_DATA = {
            "product_type": Product.CAP,
            "main_color": "Red",
            "secondary_colors": "Yellow, Blue",
            "brand": "Nike",
            "inclusion_date": str(datetime.utcnow().date()),
            "photo_url": "https://example.com/product.png",
            "unit_price": "10.99",
            "initial_stock": "90",
            "logo_color": "Black"
        }

    CAP_PRODUCT_DATA_2 = {
        "product_type": Product.CAP,
        "main_color": "Green",
        "secondary_colors": "Yellow, Blue",
        "brand": "Addidas",
        "inclusion_date": str(datetime.utcnow().date() - timedelta(days=5)),
        "photo_url": "https://example.com/product.png",
        "unit_price": "10.99",
        "initial_stock": "90",
        "logo_color": "Black"
    }

    TSHIRT_PRODUCT_DATA = {
        "product_type": Product.TSHIRT,
        "main_color": "Gray",
        "secondary_colors": "Green, White",
        "brand": "Acme",
        "inclusion_date": str(datetime.utcnow().date()),
        "photo_url": "https://example.com/tshirt.png",
        "unit_price": "10.0",
        "initial_stock": "100",
        "size": "L",
        "composition": json.dumps({"cotton": 50, "polyester": 50}),
        "gender": "Man",
        "has_sleeves": "true"
    }

    @pytest.mark.django_db
    def test_create_product(self, api_client: APIClient):
        product_data = random.choice([
            self.CAP_PRODUCT_DATA, self.TSHIRT_PRODUCT_DATA
        ])

        response = api_client.post(self.URL, data=product_data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.count() == 1
        assert Product.objects.get().main_color == product_data["main_color"]

    @pytest.mark.django_db
    def test_list_products_ordered(self, api_client: APIClient):
        api_client.post(self.URL, data=self.TSHIRT_PRODUCT_DATA)
        api_client.post(self.URL, data=self.CAP_PRODUCT_DATA_2)
        api_client.post(self.URL, data=self.CAP_PRODUCT_DATA)

        response = api_client.get(self.URL)

        assert response.status_code == status.HTTP_200_OK

        # Get the 3 products
        assert len(response.data) == 3

        # Ordered by caps first and tshirts second.
        assert response.data[0]["product_type"] == Product.CAP
        assert response.data[1]["product_type"] == Product.CAP
        assert response.data[2]["product_type"] == Product.TSHIRT

        # Ordered by inclusion date.
        assert response.data[0]["inclusion_date"] >= response.data[1]["inclusion_date"]


class TestProductRetrieveUpdateDestroy:
    URL = "http://127.0.0.1:8000/api/v1/products/%d/"

    @pytest.mark.django_db
    def test_product_retrieve(self, api_client: APIClient, cap_product: Cap, tshirt_product: Tshirt):
        product = random.choice([cap_product, tshirt_product])
        url = self.URL % product.id

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == product.id
        assert response.data["main_color"] == product.main_color

    @pytest.mark.django_db
    def test_product_update_cap(self, api_client: APIClient, cap_product: Cap):
        url = self.URL % cap_product.id

        payload = {
            "main_color": "blue",
            "logo_color": "yellow"
        }

        response = api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK

        cap_product.refresh_from_db()
        assert cap_product.id == response.data["id"]
        assert cap_product.main_color == payload["main_color"]
        assert cap_product.logo_color == payload["logo_color"]

    @pytest.mark.django_db
    def test_product_update_tshirt(self, api_client: APIClient, tshirt_product: Tshirt):
        url = self.URL % tshirt_product.id

        payload = {
            "main_color": "blue",
            "gender": "Unisex",
            "has_sleeves": "false"
        }

        response = api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK

        tshirt_product.refresh_from_db()
        assert tshirt_product.id == response.data["id"]
        assert tshirt_product.main_color == payload["main_color"]
        assert tshirt_product.gender == payload["gender"]
        assert tshirt_product.has_sleeves is False

    @pytest.mark.django_db
    def test_product_delete(self, api_client: APIClient, product: Product):
        url = self.URL % product.id

        utc_now_date = timezone.now()
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        product.refresh_from_db()
        assert product.is_deleted is True
        assert product.deleted_at >= utc_now_date


class TestCartItemCreate:
    URL = "http://127.0.0.1:8000/api/v1/add_product/"

    @pytest.mark.django_db
    def test_cart_item_create(self, api_client: APIClient, cap_product: Cap, tshirt_product: Tshirt):
        product = random.choice([cap_product, tshirt_product])

        payload = {
            "product_id": product.id,
            "quantity": random.randint(1, product.current_stock)
        }

        response = api_client.post(self.URL, data=payload)

        assert response.status_code == status.HTTP_201_CREATED

        shopping_cart = ShoppingCart.objects.get(purchased=False, created_on=datetime.utcnow().today())
        cart_item = CartItem.objects.get(product=product, shopping_cart=shopping_cart)
        assert cart_item.quantity == payload["quantity"]

    @pytest.mark.django_db
    def test_cart_item_update(self, api_client: APIClient, cart_item: CartItem):
        payload = {
            "product_id": cart_item.product.id,
            "quantity": random.randint(1, cart_item.product.current_stock - cart_item.quantity)
        }

        current_quantity = cart_item.quantity
        current_stock = cart_item.product.current_stock
        response = api_client.post(self.URL, data=payload)

        cart_item.refresh_from_db()
        assert response.status_code == status.HTTP_201_CREATED
        assert cart_item.quantity == current_quantity + payload["quantity"]
        assert cart_item.product.current_stock == current_stock - payload["quantity"]


class TestShoppingCartView:
    URL = "http://127.0.0.1:8000/api/v1/view_cart/"

    @pytest.mark.django_db
    def test_shopping_cart_retrieve_empty(self, api_client: APIClient):
        response = api_client.get(self.URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "products": [],
            "total_products": 0,
        }

    @pytest.mark.django_db
    def test_shopping_cart_retrieve(self, api_client: APIClient, cart_item: CartItem, cap_product: Cap):
        payload = {
            "product_id": cap_product.id,
            "quantity": random.randint(1, cap_product.current_stock)
        }

        api_client.post(TestCartItemCreate.URL, data=payload)

        response = api_client.get(self.URL)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["products"]) == 2
        assert response.data["total_products"] == cart_item.quantity + payload["quantity"]
        assert response.data["products"][0]["product_id"] == cart_item.product.id
        assert response.data["products"][0]["quantity"] == cart_item.quantity
        assert response.data["products"][1]["product_id"] == cap_product.id
        assert response.data["products"][1]["quantity"] == payload["quantity"]


class TestOrderView:
    URL = "http://127.0.0.1:8000/api/v1/order/"

    @pytest.mark.django_db
    def test_order_view_invalid_form(self, api_client: APIClient, cart_item: CartItem, mocker: MockerFixture):
        payload = {
            "name": "Jane",
            "last_name": "Doe",
            "address": "Barcelona, CP 08001",
            "email": "jane.doe@gmail.com",
            "mobile_number": "+34123456789"
        }
        payload.pop(random.choice(list(payload.keys())))

        mock_send_order_email = mocker.patch("utils.send_order_email")

        response = api_client.post(self.URL, data=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock_send_order_email.assert_not_called()

    @pytest.mark.django_db
    def test_order_view_without_shopping_cart(self, api_client: APIClient, mocker: MockerFixture):
        payload = {
            "name": "Jane",
            "last_name": "Doe",
            "address": "Barcelona, CP 08001",
            "email": "jane.doe@gmail.com",
            "mobile_number": "+34123456789"
        }

        mock_send_order_email = mocker.patch("utils.send_order_email")

        response = api_client.post(self.URL, data=payload)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "message" in response.data
        assert response.data["message"] == "There is no current shopping cart."
        mock_send_order_email.assert_not_called()

    @pytest.mark.django_db
    def test_order_view(self, api_client: APIClient, cart_item: CartItem, mocker: MockerFixture):
        payload = {
            "name": "Jane",
            "last_name": "Doe",
            "address": "Barcelona, CP 08001",
            "email": "jane.doe@gmail.com",
            "mobile_number": "+34123456789"
        }

        mock_send_order_email = mocker.patch("products.views.send_order_email")

        response = api_client.post(self.URL, data=payload)

        assert response.status_code == status.HTTP_200_OK
        mock_send_order_email.assert_called_once_with(payload)
        assert ShoppingCart.objects.filter(purchased=False).exists() is False
