from datetime import datetime

from django.db.models import Q, Sum

from products.models import Product, CartItem


def update_product_stock():
    products_quantity = CartItem.objects.filter(
        Q(shopping_cart__purchased=True) | Q(shopping_cart__created_on=datetime.utcnow().today())
    ).values('product_id').annotate(total=Sum('quantity'))

    for product_quantity in products_quantity:
        product = Product.objects.get(id=product_quantity["product_id"])
        product.current_stock = product.initial_stock - product_quantity["total"]
        product.save(update_fields=["current_stock"])
