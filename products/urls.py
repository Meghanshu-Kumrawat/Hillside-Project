"""Hillside_project URL Configuration
"""

from django.urls import path, include
from rest_framework import routers
from django.views.generic import RedirectView
from django.conf import settings
from products.views import ProductViewSet, ProductImageViewSet


router = routers.DefaultRouter(trailing_slash=False)
router.register('products', ProductViewSet)
router.register('products-image', ProductImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]