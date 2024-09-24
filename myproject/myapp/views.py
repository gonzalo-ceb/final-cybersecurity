# myapp/views.py
from django.contrib import messages
from django.contrib.auth import login
from django import forms
from django.shortcuts import redirect
from django.core.mail import send_mail
import random
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, CustomAuthenticationForm

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
        # Autenticación inicial
        user = form.get_user()

        # Generar OTP y enviarlo al correo electrónico
        self.send_otp(user)

        # Redirigir a la página de verificación de OTP
        return redirect('verify_otp')

    def send_otp(self, user):
        # Generar un código OTP aleatorio de 6 dígitos
        otp_code = random.randint(100000, 999999)

        # Guardar el OTP temporalmente en el modelo de usuario
        user.otp_code = otp_code
        user.save()

        # Enviar el OTP al correo electrónico del usuario
        send_mail(
            subject="Tu código de verificación OTP",
            message=f"Tu código OTP es {otp_code}.",
            from_email="sandra.gonzalez.ceb@gmail.com",
            recipient_list=[user.email],
        )

class OTPForm(forms.Form):
    otp_code = forms.IntegerField(label='Código OTP')

class VerifyOTPView(View):
    def get(self, request):
        # Mostrar el formulario de OTP
        form = OTPForm()
        return render(request, 'verify_otp.html', {'form': form})

    def post(self, request):
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_input = form.cleaned_data.get('otp')

            # Aquí verificas si el OTP es correcto
            # En este ejemplo, lo comparo con un OTP almacenado en la sesión (esto puede variar según tu lógica)
            stored_otp = request.session.get('otp_code')  # Puedes almacenar el OTP generado en la sesión al enviarlo por email o SMS

            if otp_input == stored_otp:
                # OTP correcto, continuar con el flujo de autenticación
                messages.success(request, "Código OTP verificado correctamente")
                # Redirigir a la página principal o a la siguiente fase
                return redirect('home')  # Redirige a donde desees
            else:
                # OTP incorrecto, muestra mensaje de error
                messages.error(request, "Código OTP incorrecto. Intenta de nuevo.")
                return render(request, 'verify_otp.html', {'form': form})

        return render(request, 'verify_otp.html', {'form': form})

@login_required  # Asegúrate de que el usuario esté autenticado antes de verificar OTP
def verify_otp(request):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']
            user = request.user

            # Verifica si el OTP coincide con el guardado en el modelo
            if user.otp_code == otp_code:
                # OTP correcto, autenticar completamente al usuario
                user.otp_verified = True
                user.save()
                return redirect('home')
            else:
                form.add_error('otp_code', 'El código OTP es incorrecto')
    else:
        form = OTPForm()

    return render(request, 'verify_otp.html', {'form': form})

class HomeView(TemplateView):
    template_name = 'home.html'

