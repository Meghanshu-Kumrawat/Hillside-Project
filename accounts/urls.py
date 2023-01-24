"""Hillside_project URL Configuration
"""
from django.urls import path
from accounts.views import UserRegisterView, HelloView, VerifyOtpView

urlpatterns = [
    path('register', UserRegisterView.as_view()),
    path('verify', VerifyOtpView.as_view()),
    path('', HelloView.as_view()),
]
