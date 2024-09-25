from django.urls import path
from django.contrib.auth import views as auth_views
from .views import UserRegisterView, UserLoginView, VerifyOTPView, HomeView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('home/', HomeView.as_view(), name='home'),
]
