# myapp/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, SolicitudServicio, Ruta


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'user_type')

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')

class OTPForm(forms.Form):
    otp = forms.CharField(label='Código OTP', max_length=6, widget=forms.TextInput(attrs={'placeholder': 'Introduce tu código OTP'}))

class SolicitudServicioForm(forms.ModelForm):
    class Meta:
        model = SolicitudServicio
        fields = ['ruta']

    ruta = forms.ModelChoiceField(queryset=Ruta.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control',
    }))