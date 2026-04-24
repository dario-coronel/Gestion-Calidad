from django.urls import path
from . import views

app_name = 'verificacion'

urlpatterns = [
    path('', views.lista, name='lista'),
]
