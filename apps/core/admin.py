from django.contrib import admin

from .models import Sector


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'activo')
	list_filter = ('activo',)
	search_fields = ('nombre',)

