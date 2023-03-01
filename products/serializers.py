"""Create your serializers here.
"""

import datetime

from django.db import transaction
from rest_framework import serializers

from products.models import Product, Cap, Tshirt, ShoppingCart, CartItem


class CapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cap
        fields = ["logo_color"]


class TshirtSerializer(serializers.ModelSerializer):
    gender = serializers.CharField()
    descripcion = serializers.CharField(read_only=True)

    class Meta:
        model = Tshirt
        fields = ["size", "composition", "gender", "has_sleeves", "descripcion"]

    def validate_gender(self, value: str) -> str:
        capitalized_value = value.capitalize()

        if capitalized_value not in Tshirt.GENDER_TYPES:
            raise serializers.ValidationError(f"{capitalized_value} is an invalid gender.")

        return capitalized_value


class ProductListCreateSerializer(serializers.ModelSerializer):
    product_type = serializers.CharField()
    current_stock = serializers.IntegerField(read_only=True)
    descripcion = serializers.CharField(read_only=True)
    initial_stock = serializers.IntegerField(write_only=True)

    class Meta:
        model = Product
        exclude = ("is_deleted", "deleted_at")

    def validate_product_type(self, value: str) -> str:
        capitalized_value = value.capitalize()

        if capitalized_value not in Product.PRODUCT_TYPES:
            raise serializers.ValidationError(f"{capitalized_value} is an invalid product type.")

        if self.instance and self.instance.product_type != capitalized_value:
            raise serializers.ValidationError("Product type cannot be modified.")

        return capitalized_value

    def validate_initial_stock(self, value: int) -> int:
        if value < 0:
            raise serializers.ValidationError("Initial stock cannot be negative.")
        return value

    def to_representation(self, instance: Product) -> dict:
        data = super().to_representation(instance)

        if hasattr(instance, "cap"):
            data |= CapSerializer(instance.cap).to_representation(instance.cap)
        elif hasattr(instance, "tshirt"):
            data |= TshirtSerializer(instance.tshirt).to_representation(instance.tshirt)

        return data

    def create(self, validated_data: dict) -> Cap | Tshirt:
        product_type: str = validated_data.get("product_type")
        validated_data["current_stock"] = validated_data.get("initial_stock")

        if product_type == Product.CAP:
            cap_serializer = CapSerializer(data=self.initial_data)
            cap_serializer.is_valid(raise_exception=True)
            validated_data |= cap_serializer.validated_data
            product = Cap.objects.create(**validated_data)
        elif product_type == Product.TSHIRT:
            tshirt_serializer = TshirtSerializer(data=self.initial_data)
            tshirt_serializer.is_valid(raise_exception=True)
            validated_data |= tshirt_serializer.validated_data
            product = Tshirt.objects.create(**validated_data)

        return product

class ProductRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    product_type = serializers.CharField(read_only=True)
    descripcion = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        exclude = ("is_deleted", "deleted_at", "initial_stock")

    def update(self, instance: Product, validated_data: dict) -> Cap | Tshirt:
        @transaction.atomic()
        def transactional_update() -> Cap | Tshirt:
            return super(ProductRetrieveUpdateDestroySerializer, self).update(instance, validated_data)

        product_instance = transactional_update()

        return product_instance


class ProductInCartSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="id", read_only=True)
    descripcion = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = ["product_id", "descripcion", "photo_url", "unit_price"]


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = CartItem
        fields = ("product_id", "quantity")

    def validate(self, attrs):
        product_id = attrs['product_id']
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product_id": f"Product with id {product_id} does not exist."})

        quantity = attrs['quantity']
        if quantity > product.current_stock:
            raise serializers.ValidationError({"quantity": "Not enough stock available."})

        return attrs

    def to_representation(self, instance: CartItem) -> dict:
        data = ProductInCartSerializer(instance.product).data
        data["quantity"] = instance.quantity

        return data

    def create(self, validated_data: dict) -> Cap | Tshirt:
        quantity: int = validated_data["quantity"]
        today = datetime.date.today()

        @transaction.atomic()
        def transactional():
            product: Product = Product.objects.select_for_update().get(
                id=validated_data["product_id"], is_deleted=False
            )
            shopping_cart, _ = ShoppingCart.objects.select_for_update().get_or_create(
                created_on=today, purchased=False
            )
            cart_item, _ = CartItem.objects.select_for_update().get_or_create(
                shopping_cart=shopping_cart, product=product
            )

            cart_item.quantity = max(0, cart_item.quantity + quantity)
            product.current_stock -= quantity

            cart_item.save()
            product.save()

            return cart_item

        cart_item = transactional()

        return cart_item


class OrderSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=20)
    last_name = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    mobile_number = serializers.CharField(max_length=20)
