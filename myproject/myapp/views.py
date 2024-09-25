from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import login
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import redirect, render
from django.core.mail import send_mail
import random
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, CustomAuthenticationForm


User = get_user_model()

class UserRegisterView(FormView):
    template_name = 'register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

class UserLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        user = form.get_user()

        self.request.session['otp_user_id'] = user.id

        self.send_otp(user)
        return redirect('verify_otp')

    def send_otp(self, user):
        otp_code = random.randint(100000, 999999)
        user.otp_code = otp_code
        user.otp_created_at = timezone.now()
        user.save()

        send_mail(
            subject="Tu código de verificación OTP",
            message=f"Tu código OTP es {otp_code}.",
            from_email="sandra.gonzalez.ceb@gmail.com",
            recipient_list=[user.email],
        )


class OTPForm(forms.Form):
    otp_code = forms.IntegerField(label='Código OTP')


OTP_VALIDITY_PERIOD = timedelta(minutes=10)

class VerifyOTPView(View):
    def get(self, request):
        # Mostrar el formulario de verificación de OTP
        form = OTPForm()
        return render(request, 'verify_otp.html', {'form': form})

    def post(self, request):
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_input = form.cleaned_data.get('otp_code')

            # Buscar el usuario por el ID almacenado en la sesión
            if 'otp_user_id' in request.session:
                try:
                    user = User.objects.get(id=request.session['otp_user_id'])
                except User.DoesNotExist:
                    messages.error(request, "Usuario no encontrado.")
                    return redirect('login')

                # Verificar que el código OTP no haya expirado
                if timezone.now() > user.otp_created_at + OTP_VALIDITY_PERIOD:
                    messages.error(request, "El código OTP ha expirado.")
                    return redirect('login')

                if user.otp_code == otp_input:
                    # OTP correcto, marcar como verificado
                    user.otp_verified = True
                    user.save()

                    # Iniciar sesión manualmente al usuario
                    login(request, user)

                    # Borrar el ID del usuario de la sesión
                    del request.session['otp_user_id']

                    messages.success(request, "Código OTP verificado correctamente.")
                    return redirect('home')  # Redirige a la página principal o donde prefieras
                else:
                    messages.error(request, "Código OTP incorrecto.")
            else:
                messages.error(request, "No se encontró el usuario o el código OTP ha expirado.")

        return render(request, 'verify_otp.html', {'form': form})


class HomeView(TemplateView):
    template_name = 'home.html'

