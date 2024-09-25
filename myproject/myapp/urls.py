from django.urls import path
from django.contrib.auth import views as auth_views
from .views import UserRegisterView, UserLoginView, VerifyOTPView, HomeView, logout_view, resend_otp_view

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', resend_otp_view, name='resend_otp'),
    path('', HomeView.as_view(), name='home'),
]
