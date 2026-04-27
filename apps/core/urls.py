from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('sectores/', views.sectores_lista, name='sectores_lista'),
    path('sectores/nuevo/', views.sector_crear, name='sector_crear'),
    path('sectores/<int:pk>/editar/', views.sector_editar, name='sector_editar'),
    path('sectores/<int:pk>/eliminar/', views.sector_eliminar, name='sector_eliminar'),
]

