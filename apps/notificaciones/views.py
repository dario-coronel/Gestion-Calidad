from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Notificacion


@login_required
def panel(request):
    notifs = Notificacion.objects.filter(usuario=request.user).order_by('-creada_en')[:10]
    return render(request, 'notificaciones/panel.html', {'notifs': notifs})