"""Create your views here.
"""

import datetime

from django.db.models import Case, When, Value, CharField

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
)

from products.models import Product, ShoppingCart, CartItem
from products.serializers import ProductSerializer, CartItemSerializer, OrderSerializer

from utils import send_order_email


class ProductListCreate(ListCreateAPIView):
    queryset = Product.objects.all().filter(
        is_deleted=False
    ).order_by(
        Case(
            When(product_type=Product.CAP, then=Value(1)),
            When(product_type=Product.TSHIRT, then=Value(2)),
            output_field=CharField()
        ),
        "-inclusion_date"
    )
    serializer_class = ProductSerializer


class ProductRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all().filter(is_deleted=False)
    serializer_class = ProductSerializer

    def perform_destroy(self, instance: Product):
        instance.is_deleted = True
        instance.deleted_at = datetime.datetime.utcnow()
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemCreate(CreateAPIView):
    serializer_class = CartItemSerializer


class ShoppingCartView(APIView):
    def get(self, request: Request) -> Response:
        today = datetime.date.today()

        data = {
            "products": [],
            "total_products": 0
        }
        try:
            shopping_cart = ShoppingCart.objects.get(created_on=today, purchased=False)
        except ShoppingCart.DoesNotExist:
            pass
        else:
            cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)
            data["products"] = CartItemSerializer(cart_items, many=True).data
            data["total_products"] = sum(cart_item.quantity for cart_item in cart_items)

        return Response(data)


class OrderView(APIView):
    def post(self, request: Request) -> Response:
        today = datetime.date.today()

        serializer = OrderSerializer(data=request.data)

        if not serializer.is_valid():
            # Return the validation errors in the response
            return Response(serializer.errors, status=400)

        try:
            shopping_cart = ShoppingCart.objects.get(created_on=today, purchased=False)
        except ShoppingCart.DoesNotExist:
            return Response({"message": "There is no current shopping cart"}, status=404)

        # Process the order
        shopping_cart.purchased = True
        shopping_cart.save()

        send_order_email(serializer.validated_data)

        return Response({"message": "Your order has been successfully processed."})
