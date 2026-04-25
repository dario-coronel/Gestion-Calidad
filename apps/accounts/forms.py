from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Usuario, Rol


class UsuarioCreateForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'rol', 'area', 'telefono', 'is_active'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        # Los administradores del sistema pueden entrar al admin de Django.
        user.is_staff = user.rol == Rol.ADMIN
        if commit:
            user.save()
        return user


class UsuarioUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'rol', 'area', 'telefono', 'is_active'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = user.rol == Rol.ADMIN
        if commit:
            user.save()
        return user
