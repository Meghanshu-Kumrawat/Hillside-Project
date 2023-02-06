"""Hillside_project URL Configuration
"""

from django.urls import path, include
from rest_framework import routers
from orders.views import CartViewSet, OrderConfirmationViewSet, OrderCheckoutViewSet, OrderHistoryViewSet, OrderCheckoutViewSet


router = routers.DefaultRouter(trailing_slash=False)
router.register('carts', CartViewSet)
router.register('order-confirmation', OrderConfirmationViewSet)
router.register('order-history', OrderHistoryViewSet)

urlpatterns = [
    path('order-checkout/', OrderCheckoutViewSet.as_view()),
    path('', include(router.urls))
]
