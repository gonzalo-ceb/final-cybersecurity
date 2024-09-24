from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
    path('api/', include('myapp.urls')),
    path('two-factor/', include('two_factor.urls', namespace='two_factor')),
]
