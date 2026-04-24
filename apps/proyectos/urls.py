from django.urls import path
from . import views

app_name = 'proyectos'

urlpatterns = [
    path('', views.lista, name='lista'),
]
