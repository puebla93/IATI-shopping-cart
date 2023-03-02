from datetime import datetime

from django.db.models import Q, Sum

from products.models import Product, CartItem


def update_product_stock() -> None:
    """Update the products stock getting all cart items that are in a purchased shopping cart
    or in the current shopping cart. This function is executed by a cron jobs every hour.
    """

    products_quantity = CartItem.objects.filter(
        Q(shopping_cart__purchased=True) | Q(shopping_cart__created_on=datetime.utcnow().today())
    ).values('product_id').annotate(total=Sum('quantity'))

    products = Product.objects.filter(
        id__in=[product_quantity["product_id"] for product_quantity in products_quantity]
    )

    for i, product in enumerate(products):
        product.current_stock = product.initial_stock - products_quantity[i]["total"]
        product.save(update_fields=["current_stock"])
