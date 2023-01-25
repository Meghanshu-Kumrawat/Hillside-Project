"""Hillside_project URL Configuration
"""
from django.urls import path
from accounts.views import UserRegisterView, UserLoginView, HelloView, VerifyOtpView, PasswordResetView, PasswordResetConfirmView

urlpatterns = [
    path('register', UserRegisterView.as_view()),
    path('login', UserLoginView.as_view()),
    path('verify', VerifyOtpView.as_view()),
    path('', HelloView.as_view()),
    path('password-reset', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
