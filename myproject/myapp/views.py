import json
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import login
from django import forms
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.http import BadHeaderError, JsonResponse
from django.utils import timezone
from django.shortcuts import redirect, render, get_object_or_404
from django.core.mail import send_mail
import random
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm, SolicitudServicioForm, CamionForm
from .models import SolicitudServicio, Ruta, Camion, ServicioAsignado, Cliente, Transportista

User = get_user_model()


class UserRegisterView(FormView):
    template_name = 'register.html'
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        user = form.save()

        if user.user_type == 'cliente':
            Cliente.objects.create(nombre=user.username, telefono="999999999", usuario=user)
        elif user.user_type == 'transportista':
            Transportista.objects.create(nombre=user.username, licencia_conducir="AB12345", telefono="999999999")

        messages.success(self.request, 'Se ha registrado correctamente, redirigiendo a inicio de sesión...')
        return redirect('login')


def logout_view(request):
    logout(request)

    if 'messages' in request.session:
        del request.session['messages']

    return redirect('home')


class UserLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomAuthenticationForm

    OTP_VALIDITY_PERIOD = timedelta(minutes=5)

    def form_valid(self, form):
        user = form.get_user()

        self.request.session['otp_user_id'] = user.id

        self.send_otp(user)
        return redirect('verify_otp')

    def form_invalid(self, form):
        messages.error(self.request, 'Credenciales incorrectas. Intenta de nuevo.')
        return super().form_invalid(form)

    def send_otp(self, user):
        if user.otp_created_at and timezone.now() < user.otp_created_at + self.OTP_VALIDITY_PERIOD:
            otp_code = user.otp_code
        else:
            otp_code = random.randint(100000, 999999)
            user.otp_code = otp_code
            user.otp_created_at = timezone.now()
            user.save()

        try:
            send_mail(
                subject="Tu código de verificación OTP",
                message=f"Tu código OTP es {otp_code}.",
                from_email="sandra.gonzalez.ceb@gmail.com",
                recipient_list=[user.email],
            )
        except BadHeaderError:
            messages.error(self.request, "Hubo un problema al enviar el correo de verificación. Inténtalo de nuevo.")


class OTPForm(forms.Form):
    otp_code = forms.IntegerField(label='Código OTP')


class VerifyOTPView(View):
    OTP_VALIDITY_PERIOD = timedelta(minutes=5)

    def get(self, request):
        form = OTPForm()

        user_id = request.session.get('otp_user_id')
        user = User.objects.get(id=user_id)

        expiration_time = user.otp_created_at + self.OTP_VALIDITY_PERIOD
        time_remaining = (expiration_time - timezone.now()).total_seconds()

        return render(request, 'verify_otp.html', {'form': form, 'time_remaining': int(time_remaining)})

    def post(self, request):
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_input = form.cleaned_data.get('otp_code')

            if 'otp_user_id' in request.session:
                try:
                    user = User.objects.get(id=request.session['otp_user_id'])
                except User.DoesNotExist:
                    messages.error(request, "Usuario no encontrado.")
                    return redirect('login')

                if timezone.now() > user.otp_created_at + self.OTP_VALIDITY_PERIOD:
                    messages.error(request, "El código OTP ha expirado.")
                    return redirect('login')

                if user.otp_code == otp_input:
                    user.otp_verified = True
                    user.save()

                    login(request, user)

                    del request.session['otp_user_id']

                    messages.success(request, "Código OTP verificado correctamente.")
                    return redirect('home')
                else:
                    messages.error(request, "Código OTP incorrecto.")
            else:
                messages.error(request, "No se encontró el usuario o el código OTP ha expirado.")

        return render(request, 'verify_otp.html', {'form': form})


def resend_otp_view(request):
    user_id = request.session.get('otp_user_id')

    if not user_id:
        return JsonResponse({'error': 'No se encontró el usuario.'}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado.'}, status=404)

    otp_code = random.randint(100000, 999999)
    user.otp_code = otp_code
    user.otp_created_at = timezone.now()
    user.save()

    send_mail(
        subject="Tu nuevo código de verificación OTP",
        message=f"Tu nuevo código OTP es {otp_code}.",
        from_email="sandra.gonzalez.ceb@gmail.com",
        recipient_list=[user.email],
    )

    return JsonResponse({'message': 'Nuevo OTP enviado con éxito.', 'time_remaining': 300})


class HomeView(TemplateView):
    template_name = 'home.html'


@login_required
def crear_solicitud(request):
    form = SolicitudServicioForm()
    solicitudes = SolicitudServicio.objects.filter(cliente=request.user)

    if request.method == 'POST':
        form = SolicitudServicioForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.cliente = request.user
            solicitud.estado = 'pendiente'

            precio_oficial = request.POST.get('precio_oficial')
            if precio_oficial:
                solicitud.precio = Decimal(precio_oficial)

            solicitud.save()

            messages.success(request,
                             f'Solicitud enviada correctamente. Número de seguimiento: {solicitud.numero_seguimiento}')
            return redirect('crear_solicitud')

    return render(request, 'solicitud_servicio.html', {'form': form, 'solicitudes': solicitudes})


def get_distancia_ruta(request, ruta_id):
    try:
        ruta = Ruta.objects.get(id=ruta_id)
        return JsonResponse({'distancia': str(ruta.distancia_km)})
    except Ruta.DoesNotExist:
        return JsonResponse({'error': 'Ruta no encontrada'}, status=404)


@login_required
def rastrear_solicitud(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id_solicitud = data.get('id_solicitud')

            if not id_solicitud:
                return JsonResponse({'error': 'Número de solicitud no proporcionado.'}, status=400)

            solicitud = SolicitudServicio.objects.get(numero_seguimiento=id_solicitud)
            return JsonResponse({
                'success': True,
                'numero_seguimiento': solicitud.numero_seguimiento,
                'estado': solicitud.estado,
                'peso': float(solicitud.peso),
                'precio': float(solicitud.precio),
                'ruta_origen': solicitud.ruta.origen,
                'ruta_destino': solicitud.ruta.destino
            })

        except SolicitudServicio.DoesNotExist:
            return JsonResponse({'error': 'Solicitud no encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido.'}, status=405)


@login_required
def transportista_solicitudes(request):
    if request.user.user_type != 'transportista':
        return redirect('home')

    try:
        transportista = Transportista.objects.get(nombre=request.user.username)
    except Transportista.DoesNotExist:
        messages.error(request, "No se ha encontrado un transportista asociado a tu cuenta.")
        return redirect('home')

    solicitudes_pendientes = SolicitudServicio.objects.filter(estado='pendiente')

    solicitudes_aceptadas = ServicioAsignado.objects.filter(transportista=transportista)

    camiones = Camion.objects.filter(transportista=transportista)

    if request.method == 'POST':
        camion_id = request.POST.get('camion')
        camion = Camion.objects.get(id=camion_id)
        solicitud_id = request.POST.get('solicitud_id')
        solicitud = SolicitudServicio.objects.get(id=solicitud_id)

        ServicioAsignado.objects.create(solicitud=solicitud, camion=camion, transportista=transportista)
        solicitud.estado = 'asignado'
        solicitud.save()

        messages.success(request, f'Solicitud {solicitud.id} asignada al camión {camion.matricula}.')
        return redirect('transportista_solicitudes')

    return render(request, 'transportista_solicitudes.html', {
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_aceptadas': solicitudes_aceptadas,
        'camiones': camiones
    })


@login_required
def transportista_aceptar_solicitud(request, solicitud_id):
    if request.user.user_type != 'transportista':
        messages.error(request, "No tienes permiso para aceptar solicitudes.")
        return redirect('transportista_solicitudes')

    try:
        transportista = Transportista.objects.get(nombre=request.user.username)
    except Transportista.DoesNotExist:
        messages.error(request, "No se ha encontrado un transportista asociado a tu cuenta.")
        return redirect('transportista_solicitudes')

    solicitud = get_object_or_404(SolicitudServicio, id=solicitud_id, estado='pendiente')

    camiones = Camion.objects.filter(transportista=transportista)

    if request.method == 'POST':
        camion_id = request.POST.get('camion')
        camion = get_object_or_404(Camion, id=camion_id, transportista=transportista)

        servicio_asignado = ServicioAsignado.objects.create(
            solicitud=solicitud,
            camion=camion,
            transportista=transportista
        )

        solicitud.estado = 'asignado'
        solicitud.save()

        messages.success(request,
                         f"Solicitud {solicitud.id} ha sido aceptada y se ha asignado el camión {camion.matricula}.")
        return redirect('transportista_solicitudes')

    return render(request, 'transportista_aceptar_solicitud.html', {'solicitud': solicitud, 'camiones': camiones})


def calcular_precio_oficial(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ruta_id = data.get('ruta_id')
            peso = Decimal(data.get('peso'))

            ruta = Ruta.objects.get(id=ruta_id)

            precio_por_km = Decimal('0.15')
            precio_por_kg = Decimal('2')
            distancia = ruta.distancia_km
            precio_oficial = (distancia * precio_por_km) + (peso * precio_por_kg)

            return JsonResponse({'precio_oficial': precio_oficial}, status=200)
        except Ruta.DoesNotExist:
            return JsonResponse({'error': 'Ruta no encontrada'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def add_camion(request):
    if request.user.user_type != 'transportista':
        return redirect('home')

    # Obtener el transportista
    try:
        transportista = Transportista.objects.get(nombre=request.user.username)
    except Transportista.DoesNotExist:
        messages.error(request, "No se ha encontrado un transportista asociado a tu cuenta.")
        return redirect('home')

    if request.method == 'POST':
        form = CamionForm(request.POST)
        if form.is_valid():
            camion = form.save(commit=False)
            camion.transportista = transportista
            camion.save()
            messages.success(request, f'Camión {camion.matricula} añadido correctamente.')
            return redirect('transportista_solicitudes')
    else:
        form = CamionForm()

    return render(request, 'add_camion.html', {'form': form})
