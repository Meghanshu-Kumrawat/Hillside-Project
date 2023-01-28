"""Hillside_project URL Configuration
"""

from django.urls import path, include
from rest_framework import routers
from orders.views import CartViewSet


router = routers.DefaultRouter(trailing_slash=False)
router.register('carts', CartViewSet)

urlpatterns = router.urls