"""Hillside_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('api/', include('products.urls')),
    path('api/', include('orders.urls')),

    # documentation for API
    path('api/schema/', SpectacularAPIView.as_view(
        permission_classes=[] # This endpoint is available for everyone
    ), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(
        url_name='schema',
        permission_classes=[] # This endpoint is available for everyone
    ), name='swagger'),
    path('api/docs/', SpectacularRedocView.as_view(
        url_name='schema',
        permission_classes=[] # This endpoint is available for everyone
    ), name='redoc'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 