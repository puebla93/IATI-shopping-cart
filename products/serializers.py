"""Create your serializers here.
"""

import datetime

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


class ProductSerializer(serializers.ModelSerializer):
    product_type = serializers.CharField()
    current_stock = serializers.IntegerField(required=False)
    descripcion = serializers.CharField(read_only=True)
    initial_stock = serializers.IntegerField(write_only=True, required=False, default=None)

    class Meta:
        model = Product
        exclude = ("is_deleted", "deleted_at")

    def validate_product_type(self, value: str) -> str:
        capitalized_value = value.capitalize()

        if capitalized_value not in Product.PRODUCT_TYPES:
            raise serializers.ValidationError(f"{capitalized_value} is an invalid product type.")

        if self.instance and self.instance.product_type != capitalized_value:
            raise serializers.ValidationError("Product type cannot be modified")

        return capitalized_value

    def validate_initial_stock(self, value: int) -> int:
        if self.instance and value is not None:
            raise serializers.ValidationError("Initial stock cannot be modified")
        if value is None and not self.instance:
            self.fail("required")
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

    def update(self, instance: Product, validated_data: dict):
        validated_data.pop("initial_stock", None)
        return super().update(instance, validated_data)


class ProductInCartSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="id", read_only=True)
    descripcion = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = ["product_id", "descripcion", "photo_url", "unit_price"]


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.JSONField()
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = CartItem
        exclude = ("id", "shopping_cart")

    def validate_product(self, value: dict) -> dict:
        product_id = value.get("id", None)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError(f"{product_id} is an invalid product id.")

        return product

    def to_representation(self, instance: CartItem) -> dict:
        data = ProductInCartSerializer(instance.product).data
        data["quantity"] = instance.quantity

        return data

    def create(self, validated_data: dict) -> Cap | Tshirt:
        today = datetime.date.today()
        product: Product = validated_data["product"]
        quantity: int = validated_data["quantity"]
        try:
            shopping_cart = ShoppingCart.objects.get(created_on=today, purchased=False)
        except ShoppingCart.DoesNotExist:
            shopping_cart = ShoppingCart.objects.create(created_on=today)

        try:
            cart_item = CartItem.objects.get(shopping_cart=shopping_cart, product=product)
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(shopping_cart=shopping_cart, product=product, quantity=quantity)
        else:
            cart_item += quantity
            cart_item.save()

        product.current_stock -= quantity
        product.save()

        return cart_item
