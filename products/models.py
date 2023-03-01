"""Create your models here.
"""

from django.db import models
from django.core.exceptions import ValidationError


def validate_tshirt_materials(composition: dict[str, float]) -> None:
    """Validate the composition of a T-shirt.

    Given a composition dictionary that maps material names to their percentage in
    the T-shirt, this function checks that all materials are valid according to the
    Tshirt.VALID_MATERIALS list. If there are invalid materials, a ValidationError is
    raised with a message listing the invalid materials.

    Args:
        composition (dict[str, float]): A dictionary mapping material names (strings)
        to their percentage (float) in the T-shirt composition.

    Raises:
        ValidationError: If any of the materials in the composition is not valid.
    """

    invalid_materials = set(composition) - set(Tshirt.VALID_MATERIALS)
    if invalid_materials:
        all_invalid_materials = ", ".join(invalid_materials).capitalize()
        raise ValidationError(f"{all_invalid_materials} are not valid materials.")


def validate_percentages_sum(composition: dict[str, float]) -> None:
    """Validates that the sum of the percentages in the given composition dictionary is exactly 100.

    Args:
        composition (dict[str, float]): The composition of a product, where keys are the material names
        (e.g. "cotton", "linen", etc.) and values are the corresponding percentages.

    Raises:
        ValidationError: If the sum of the percentages in the composition dictionary is not equal to 100.
    """

    suma_porcentajes = sum(composition.values())
    if suma_porcentajes != 100:
        raise ValidationError("The sum of the composition's percentage must be 100.")


class Product(models.Model):
    """Model that defines all products.
    """

    CAP = "Cap"
    TSHIRT = "Tshirt"

    PRODUCT_TYPES = [CAP, TSHIRT]

    PRODUCT_CHOICES = ((product_type, product_type) for product_type in PRODUCT_TYPES)

    product_type = models.CharField(max_length=20, editable=False, choices=PRODUCT_CHOICES)
    main_color = models.CharField(max_length=20)
    secondary_colors = models.CharField(max_length=200)
    brand = models.CharField(max_length=50)
    inclusion_date = models.DateField()
    photo_url = models.URLField()
    unit_price = models.DecimalField(max_digits=4, decimal_places=2)
    initial_stock = models.PositiveIntegerField(editable=False)
    current_stock = models.PositiveIntegerField()
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    @property
    def descripcion(self) -> str:
        descripcion = f"{self.main_color} {self.brand} {self.get_product_type_display()} with secondary colors "\
                      f"{self.secondary_colors}, included in the catalog in the year {self.inclusion_date.year}"
        return descripcion


class Cap(Product):
    """Model that defines cap products.
    """

    logo_color = models.CharField(max_length=20)


class Tshirt(Product):
    """Model that defines t-shirt products.
    """

    MAN = "Man"
    WOMAN = "Woman"
    UNISEX = "Unisex"

    GENDER_TYPES = [MAN, WOMAN, UNISEX]

    GENDER_CHOICES = ((gender, gender) for gender in GENDER_TYPES)

    VALID_MATERIALS = [
        "cotton", "linen", "hemp",
        "polyester", "nylon", "wool",
        "silk"
    ]

    size = models.CharField(max_length=20)
    composition = models.JSONField(
        validators=[
            validate_tshirt_materials,
            validate_percentages_sum
        ]
    )
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    has_sleeves = models.BooleanField()

    @property
    def descripcion(self):
        descripcion = f"{super().descripcion}, size {self.size}, composition {self.composition_display}"
        return descripcion

    @property
    def composition_display(self):
        return ", ".join([f"{m}: {p}%" for m, p in self.composition.items()])


class ShoppingCart(models.Model):
    purchased = models.BooleanField(default=False)
    created_on = models.DateField(auto_now_add=True)


class CartItem(models.Model):
    shopping_cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
