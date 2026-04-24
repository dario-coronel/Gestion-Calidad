from django.urls import path
from . import views

app_name = 'om'

urlpatterns = [
    path('', views.lista, name='lista'),
]
