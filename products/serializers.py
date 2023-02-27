"""Create your serializers here.
"""

from rest_framework import serializers

from .models import Product, Cap, Tshirt


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
