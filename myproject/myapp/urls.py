from django.urls import path
from . import views
from .views import UserRegisterView, UserLoginView

urlpatterns = [
    # path('', home_view, name='home'),
    # path('clientes/', views.ClienteListCreate.as_view(), name='cliente-list-create'),
    # path('clientes/<int:pk>/', views.ClienteDetail.as_view(), name='cliente-detail'),
    # path('transportistas/', views.TransportistaListCreate.as_view(), name='transportista-list-create'),
    # path('transportistas/<int:pk>/', views.TransportistaDetail.as_view(), name='transportista-detail'),
    # path('camiones/', views.CamionListCreate.as_view(), name='camion-list-create'),
    # path('camiones/<int:pk>/', views.CamionDetail.as_view(), name='camion-detail'),
    # path('rutas/', views.RutaListCreate.as_view(), name='ruta-list-create'),
    # path('rutas/<int:pk>/', views.RutaDetail.as_view(), name='ruta-detail'),
    # path('solicitudes/', views.SolicitudServicioListCreate.as_view(), name='solicitud-list-create'),
    # path('solicitudes/<int:pk>/', views.SolicitudServicioDetail.as_view(), name='solicitud-detail'),
    # path('servicios/', views.ServicioAsignadoListCreate.as_view(), name='servicio-list-create'),
    # path('servicios/<int:pk>/', views.ServicioAsignadoDetail.as_view(), name='servicio-detail'),
    # path('facturas/', views.FacturaListCreate.as_view(), name='factura-list-create'),
    # path('facturas/<int:pk>/', views.FacturaDetail.as_view(), name='factura-detail'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
]
