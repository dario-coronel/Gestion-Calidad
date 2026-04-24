from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'get_full_name', 'rol', 'area', 'is_active')
    list_filter = ('rol', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('SGC', {'fields': ('rol', 'area', 'telefono')}),
    )

