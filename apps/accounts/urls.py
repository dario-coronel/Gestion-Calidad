from django.urls import path
from .views import SGCLoginView, SGCLogoutView

app_name = 'accounts'

urlpatterns = [
    path('login/', SGCLoginView.as_view(), name='login'),
    path('logout/', SGCLogoutView.as_view(), name='logout'),
]
