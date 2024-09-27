# myapp/forms.py
from decimal import Decimal

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, SolicitudServicio, Ruta

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type', 'password1', 'password2']


    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['user_type'].widget.attrs.update({'class': 'form-control'})


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')


class OTPForm(forms.Form):
    otp = forms.CharField(label='Código OTP', max_length=6,
                          widget=forms.TextInput(attrs={'placeholder': 'Introduce tu código OTP'}))


class SolicitudServicioForm(forms.ModelForm):
    class Meta:
        model = SolicitudServicio
        fields = ['ruta', 'peso']  # Incluye el campo de peso

    def clean_peso(self):
        peso = self.cleaned_data.get('peso')
        if peso:
            return Decimal(peso)  # Asegúrate de que el peso se maneje como Decimal
        return peso
