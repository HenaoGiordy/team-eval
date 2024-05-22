import re
from django import forms
from django.contrib.auth.forms import PasswordChangeForm


class UsernameForm(forms.Form):
    username = forms.CharField(label='Código o Número de Documento', 
                               max_length=150,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su código', 'required' : 'true', "type" : "number"})
                               )
    def clean_username(self):
        username = self.cleaned_data['username']
        if not username:
            raise forms.ValidationError("Por favor, ingresa un nombre de usuario.")
        if not re.match(r'^[0-9]+$', username):
            raise forms.ValidationError("Por favor, ingresa un código válido (solo números).")
        return username

class MinimalPasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label="Contraseña antigua",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'current-password'}),
    )
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('La contraseña antigua es incorrecta.')
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data["new_password1"])
        if commit:
            self.user.save()
        return self.user