"""Hillside_project URL Configuration
"""

from django.urls import path, include
from rest_framework import routers
from orders.views import CartViewSet, OrderConfirmationViewSet, OrderCheckoutViewSet, OrderHistoryViewSet


router = routers.DefaultRouter(trailing_slash=False)
router.register('carts', CartViewSet)
router.register('order-confirmation', OrderConfirmationViewSet)
router.register('order-history', OrderHistoryViewSet)

urlpatterns = [
    path('order', OrderCheckoutViewSet.as_view()),
    path('', include(router.urls))
]
