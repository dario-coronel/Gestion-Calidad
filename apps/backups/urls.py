from django.urls import path
from . import views

app_name = 'backups'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('realizar/', views.realizar_backup, name='realizar'),
    path('<int:pk>/descargar/', views.descargar_backup, name='descargar'),
]
