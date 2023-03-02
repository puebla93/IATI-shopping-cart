"""Create your views here.
"""

from datetime import datetime

from django.db import transaction
from django.db.models import Case, When, Value, CharField

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, GenericAPIView
)

from products.models import Product, ShoppingCart, CartItem
from products.serializers import (
    ProductListCreateSerializer, ProductRetrieveUpdateDestroySerializer, CartItemSerializer, OrderSerializer
)

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
    serializer_class = ProductListCreateSerializer


class ProductRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all().filter(is_deleted=False)
    serializer_class = ProductRetrieveUpdateDestroySerializer

    def perform_destroy(self, instance: Product):
        instance.is_deleted = True
        instance.deleted_at = datetime.utcnow()
        instance.save(update_fields=["is_deleted", "deleted_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemCreate(CreateAPIView):
    serializer_class = CartItemSerializer


class ShoppingCartView(GenericAPIView):
    def get(self, request: Request) -> Response:
        today = datetime.utcnow().today()

        data = {}
        try:
            shopping_cart = ShoppingCart.objects.get(created_on=today, purchased=False)
        except ShoppingCart.DoesNotExist:
            data["products"] = []
            data["total_products"] = 0
        else:
            cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)
            data["products"] = CartItemSerializer(cart_items, many=True).data
            data["total_products"] = sum(cart_item.quantity for cart_item in cart_items)

        return Response(data)


class OrderView(GenericAPIView):
    serializer_class = OrderSerializer

    def post(self, request: Request) -> Response:
        today = datetime.utcnow().today()

        serializer = OrderSerializer(data=request.data)

        if not serializer.is_valid():
            # Return the validation errors in the response
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        @transaction.atomic()
        def transactional_order():
            shopping_cart = ShoppingCart.objects.select_for_update().get(created_on=today, purchased=False)

            # Process the order
            shopping_cart.purchased = True
            shopping_cart.save(update_fields=["purchased"])

        try:
            transactional_order()
        except ShoppingCart.DoesNotExist:
            return Response({"message": "There is no current shopping cart."}, status=status.HTTP_404_NOT_FOUND)

        send_order_email(serializer.validated_data)

        return Response({"message": "Your order has been successfully processed."}, status=status.HTTP_200_OK)
