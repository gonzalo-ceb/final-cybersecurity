# myapp/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('cliente', 'Cliente'),
        ('transportista', 'Transportista'),
    )
    user_type = models.CharField(max_length=15, choices=USER_TYPES, default='cliente')

    # Almacena el código OTP temporal
    otp_code = models.IntegerField(null=True, blank=True)

    # Bandera para saber si el OTP ha sido verificado
    otp_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class Transportista(models.Model):
    nombre = models.CharField(max_length=100)
    licencia_conducir = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15)

    def __str__(self):
        return self.nombre

class Camion(models.Model):
    matricula = models.CharField(max_length=10, unique=True)
    capacidad = models.DecimalField(max_digits=10, decimal_places=2)
    transportista = models.ForeignKey(Transportista, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.matricula} - {self.transportista.nombre}"

class Ruta(models.Model):
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    distancia_km = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.origen} -> {self.destino}"

class SolicitudServicio(models.Model):
    cliente = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    fecha_solicitud = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('asignado', 'Asignado'), ('cancelado', 'Cancelado'), ('cerrado', 'Cerrado')])

    def __str__(self):
        return f"Solicitud {self.id} - {self.cliente.username} ({self.estado})"

class ServicioAsignado(models.Model):
    solicitud = models.OneToOneField(SolicitudServicio, on_delete=models.CASCADE)
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    transportista = models.ForeignKey(Transportista, on_delete=models.CASCADE)
    fecha_asignacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Servicio {self.solicitud.id} asignado a {self.camion.matricula} ({self.transportista.nombre})"

class Factura(models.Model):
    solicitud = models.OneToOneField(SolicitudServicio, on_delete=models.CASCADE)
    fecha_factura = models.DateField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Factura {self.id} - Total: {self.total}"


