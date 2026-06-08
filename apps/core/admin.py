from django.contrib import admin

from .models import Sector, Clasificacion, Responsable


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'activo')
	list_filter = ('activo',)
	search_fields = ('nombre',)


@admin.register(Clasificacion)
class ClasificacionAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'activo')
	list_filter = ('activo',)
	search_fields = ('nombre',)


@admin.register(Responsable)
class ResponsableAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'email', 'activo', 'usuario')
	list_filter = ('activo',)
	search_fields = ('nombre', 'email', 'usuario__username', 'usuario__first_name', 'usuario__last_name')

