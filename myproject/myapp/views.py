from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import login
from django import forms
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import BadHeaderError, JsonResponse
from django.utils import timezone
from django.shortcuts import redirect, render
from django.core.mail import send_mail
import random
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import SolicitudServicio, Ruta

User = get_user_model()

class UserRegisterView(FormView):
    template_name = 'register.html'
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        form.save()

        messages.success(self.request, 'Se ha registrado correctamente, redirigiendo a inicio de sesión...')

        return self.render_to_response(self.get_context_data(form=form))

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
    if request.method == "POST":
        origen_id = request.POST.get("origen")
        destino_id = request.POST.get("destino")
        ruta = Ruta.objects.filter(id=origen_id).first()

        if ruta:
            nueva_solicitud = SolicitudServicio(
                cliente=request.user,
                ruta=ruta,
                estado='pendiente'
            )
            nueva_solicitud.save()
            return redirect('solicitud_exitosa')
        else:
            return render(request, 'solicitud_servicio.html', {'rutas': Ruta.objects.all(), 'error': 'Ruta no encontrada'})

    rutas = Ruta.objects.all()
    return render(request, 'solicitud_servicio.html', {'rutas': rutas})