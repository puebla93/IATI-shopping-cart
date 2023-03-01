"""Create your urls here.
"""

from django.urls import re_path
from products import views

urlpatterns = [
    re_path(r"^products/$", views.ProductListCreate.as_view(), name="product-list-create"),
    re_path(
        r"^products/(?P<pk>[0-9]+)/$", views.ProductRetrieveUpdateDestroy.as_view(),
        name="product-retrieve-update-destroy"
    ),
    re_path(
        r"^add_product/$", views.CartItemCreate.as_view(),
        name="add-product-view"
    ),
    re_path(
        r"^view_cart/$", views.ShoppingCartView.as_view(),
        name="add-product-view"
    ),
    re_path(
        r"^order/$", views.OrderView.as_view(),
        name="order-view"
    ),
]
