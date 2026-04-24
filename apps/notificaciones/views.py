import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Notificacion


@login_required
def panel(request):
    """
    Para HTMX (campana): devuelve el partial del dropdown.
    Para acceso directo: devuelve la página completa.
    """
    notifs = Notificacion.objects.filter(usuario=request.user)

    if request.htmx:
        # Marca las últimas 10 como entregadas (no leídas aún, solo las muestra)
        recientes = notifs.order_by('-creada_en')[:10]
        return render(request, 'notificaciones/partials/campana.html', {
            'notifs': recientes,
        })

    # Página completa paginada
    page_obj = Paginator(notifs.order_by('-creada_en'), 20).get_page(
        request.GET.get('page', 1)
    )
    return render(request, 'notificaciones/lista.html', {'page_obj': page_obj})


@login_required
@require_POST
def marcar_leida(request, pk):
    notif = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    notif.marcar_leida()

    if request.htmx:
        resp = render(request, 'notificaciones/partials/item_notif.html', {'n': notif})
        resp['HX-Trigger'] = json.dumps({'showToast': {'message': 'Notificación marcada como leída', 'level': 'success'}})
        return resp

    if notif.url_destino:
        return redirect(notif.url_destino)
    return redirect('notificaciones:lista')


@login_required
@require_POST
def marcar_todas(request):
    Notificacion.objects.filter(usuario=request.user, leida=False).update(
        leida=True,
        leida_en=timezone.now(),
    )
    if request.htmx:
        resp = render(request, 'notificaciones/partials/campana.html', {'notifs': []})
        resp['HX-Trigger'] = json.dumps({'showToast': {'message': 'Todas las notificaciones marcadas como leídas', 'level': 'success'}})
        return resp
    return redirect('notificaciones:lista')
