from django.core.management.base import BaseCommand
from myapp.models import Ruta


class Command(BaseCommand):
    help = 'Carga las rutas entre ciudades (ida y vuelta) en la base de datos'

    def handle(self, *args, **kwargs):
        rutas = [
            # Rutas desde Madrid
            {"origen": "Madrid", "destino": "Barcelona", "distancia_km": 620},
            {"origen": "Madrid", "destino": "Valencia", "distancia_km": 355},
            {"origen": "Madrid", "destino": "Sevilla", "distancia_km": 530},
            {"origen": "Madrid", "destino": "Zaragoza", "distancia_km": 315},
            {"origen": "Madrid", "destino": "Málaga", "distancia_km": 530},
            {"origen": "Madrid", "destino": "Bilbao", "distancia_km": 395},
            {"origen": "Madrid", "destino": "Alicante", "distancia_km": 420},
            {"origen": "Madrid", "destino": "Granada", "distancia_km": 420},
            {"origen": "Madrid", "destino": "Murcia", "distancia_km": 400},
            {"origen": "Madrid", "destino": "Valladolid", "distancia_km": 195},

            # Rutas desde Barcelona
            {"origen": "Barcelona", "destino": "Valencia", "distancia_km": 350},
            {"origen": "Barcelona", "destino": "Sevilla", "distancia_km": 1000},
            {"origen": "Barcelona", "destino": "Zaragoza", "distancia_km": 300},
            {"origen": "Barcelona", "destino": "Málaga", "distancia_km": 970},
            {"origen": "Barcelona", "destino": "Bilbao", "distancia_km": 610},
            {"origen": "Barcelona", "destino": "Alicante", "distancia_km": 520},
            {"origen": "Barcelona", "destino": "Granada", "distancia_km": 850},

            # Rutas desde Sevilla
            {"origen": "Sevilla", "destino": "Valencia", "distancia_km": 660},
            {"origen": "Sevilla", "destino": "Málaga", "distancia_km": 205},
            {"origen": "Sevilla", "destino": "Bilbao", "distancia_km": 825},
            {"origen": "Sevilla", "destino": "Granada", "distancia_km": 250},

            # Rutas desde Valencia
            {"origen": "Valencia", "destino": "Bilbao", "distancia_km": 620},
            {"origen": "Valencia", "destino": "Málaga", "distancia_km": 640},
            {"origen": "Valencia", "destino": "Zaragoza", "distancia_km": 310},

            # Rutas desde Málaga
            {"origen": "Málaga", "destino": "Granada", "distancia_km": 125},
            {"origen": "Málaga", "destino": "Murcia", "distancia_km": 400},

            # Rutas desde Bilbao
            {"origen": "Bilbao", "destino": "Zaragoza", "distancia_km": 310},

            # Rutas desde Murcia
            {"origen": "Murcia", "destino": "Alicante", "distancia_km": 80}
        ]

        # Insertar rutas de ida
        for ruta in rutas:
            Ruta.objects.get_or_create(
                origen=ruta['origen'],
                destino=ruta['destino'],
                distancia_km=ruta['distancia_km']
            )

        # Insertar rutas de vuelta (invertir origen y destino)
        for ruta in rutas:
            Ruta.objects.get_or_create(
                origen=ruta['destino'],
                destino=ruta['origen'],
                distancia_km=ruta['distancia_km']
            )

        self.stdout.write(self.style.SUCCESS('Rutas de ida y vuelta cargadas exitosamente'))
