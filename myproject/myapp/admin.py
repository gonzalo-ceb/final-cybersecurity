from django.contrib import admin
from .models import CustomUser, Transportista, Camion, Ruta, SolicitudServicio, ServicioAsignado, Factura

# Registrar cada uno de los modelos
admin.site.register(CustomUser)
admin.site.register(Transportista)
admin.site.register(Camion)
admin.site.register(Ruta)
admin.site.register(SolicitudServicio)
admin.site.register(ServicioAsignado)
admin.site.register(Factura)

