"""Hillside_project URL Configuration
"""

from django.urls import path, include
from rest_framework import routers
from products.views import ProductBannerViewSet, ProductViewSet, BrandViewSet, CategoryViewSet, CollectionViewSet, HomeEditView


router = routers.DefaultRouter(trailing_slash=False)
router.register('banner-images', ProductBannerViewSet)
router.register('brands', BrandViewSet)
router.register('categories', CategoryViewSet)
router.register('products', ProductViewSet)
router.register('collections', CollectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('home-edit', HomeEditView.as_view()),
]