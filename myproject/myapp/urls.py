from django.urls import path
from . import views
from .views import UserRegisterView, UserLoginView, VerifyOTPView, HomeView, logout_view, resend_otp_view, \
    rastrear_solicitud, get_distancia_ruta, calcular_precio_oficial, add_camion, descargar_factura

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', resend_otp_view, name='resend_otp'),
    path('', HomeView, name='home'),
    path('solicitud/', views.crear_solicitud, name='crear_solicitud'),
    path('api/rastrear-solicitud/', rastrear_solicitud, name='rastrear_solicitud'),
    path('api/calcular-precio-oficial/', calcular_precio_oficial, name='calcular_precio_oficial'),
    path('transportista/solicitudes/', views.transportista_solicitudes, name='transportista_solicitudes'),
    path('transportista/solicitudes/aceptar/<int:solicitud_id>/', views.transportista_aceptar_solicitud, name='transportista_aceptar_solicitud'),
    path('api/get-distancia-ruta/<int:ruta_id>/', get_distancia_ruta, name='get_distancia_ruta'),
    path('transportista/add_camion/', add_camion, name='transportista_add_camion'),
    path('factura/<int:factura_id>/descargar/', descargar_factura, name='descargar_factura'),
]
