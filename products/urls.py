"""Create your urls here.
"""

from django.urls import re_path
from products import views

urlpatterns = [
    re_path(r"^products/$", views.ProductListCreate.as_view(), name="product_list_create"),
    re_path(
        r"^products/(?P<pk>[0-9]+)/$", views.ProductRetrieveUpdateDestroy.as_view(),
        name="product_retrieve_update_destroy"
    ),
    re_path(
        r"^add_product/$", views.CartItemCreate.as_view(),
        name="add_product_view"
    ),
    re_path(
        r"^view_cart/$", views.ShoppingCartView.as_view(),
        name="add_product_view"
    ),
]
