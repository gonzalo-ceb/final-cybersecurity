# myapp/forms.py
from decimal import Decimal

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, SolicitudServicio, Ruta, Camion


class CustomUserCreationForm(UserCreationForm):
    acepta_terminos = forms.BooleanField(required=True, label="Acepto los términos y condiciones")
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['user_type'].widget.attrs.update({'class': 'form-control'})
        self.fields['acepta_terminos'].widget.attrs.update({'class': 'form-check-input'})


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
        fields = ['ruta', 'peso']

    ruta = forms.ModelChoiceField(
        queryset=Ruta.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean_peso(self):
        peso = self.cleaned_data.get('peso')
        if not peso or peso <= 0:
            raise forms.ValidationError('Debes ingresar un peso válido mayor que cero.')
        return Decimal(peso)

class CamionForm(forms.ModelForm):
    class Meta:
        model = Camion
        fields = ['matricula', 'capacidad']

        widgets = {
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'matricula': 'Matrícula',
            'capacidad': 'Capacidad (kg)',
        }

class ContactForm(forms.Form):
    nombre = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Nombre'}))
    apellidos = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Apellidos'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    consulta = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Mensaje'}), required=False)
