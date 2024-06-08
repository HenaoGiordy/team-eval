import re
from django import forms
from django.contrib.auth.forms import PasswordChangeForm


class UsernameForm(forms.Form):
    username = forms.CharField(label='Ingrese su código o No.Documento', 
                               max_length=150,
                               widget=forms.TextInput(attrs={'class': 'form-control mt-2 text-center', 'placeholder': 'Código o documento', 'required' : 'true', "type" : "text"})
                               )
    

class MinimalPasswordChangeForm(forms.Form):
    
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña', 'autocomplete': 'new-password'}),
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirma contraseña', 'autocomplete': 'new-password'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    

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
