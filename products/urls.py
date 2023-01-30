"""Hillside_project URL Configuration
"""

from django.urls import path, include
from rest_framework import routers
from products.views import ProductBannerViewSet, ProductViewSet, BrandViewSet


router = routers.DefaultRouter(trailing_slash=False)
router.register('banner-images', ProductBannerViewSet)
router.register('brands', BrandViewSet)
router.register('products', ProductViewSet)

urlpatterns = router.urls
