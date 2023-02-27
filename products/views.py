"""Create your views here.
"""

import datetime

from django.db.models import Case, When, Value, CharField

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from products.models import Product
from products.serializers import ProductSerializer


class ProductListCreate(ListCreateAPIView):
    queryset = Product.objects.all().filter(
        is_deleted=False
    ).order_by(
        Case(
            When(product_type=Product.CAP, then=Value(1)),
            When(product_type=Product.TSHIRT, then=Value(2)),
            output_field=CharField()
        ),
        "inclusion_date"
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
