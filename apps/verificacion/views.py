from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import VerificacionEficacia, EstadoVerificacion
from .forms import VerificacionForm


COLORES_ESTADO = {
    EstadoVerificacion.PENDIENTE:   'bg-warning/10 text-warning',
    EstadoVerificacion.EN_REVISION: 'bg-blue-50 text-blue-700',
    EstadoVerificacion.EFICAZ:      'bg-success/10 text-success',
    EstadoVerificacion.NO_EFICAZ:   'bg-danger/10 text-danger',
}


@login_required
def lista(request):
    qs = VerificacionEficacia.objects.filter(eliminado=False).select_related('proyecto', 'responsable')

    estado = request.GET.get('estado', '')
    if estado:
        qs = qs.filter(estado=estado)

    return render(request, 'verificacion/lista.html', {
        'verificaciones': qs,
        'colores_estado': COLORES_ESTADO,
        'estados': EstadoVerificacion.choices,
        'filtros': {'estado': estado},
    })


@login_required
def detalle(request, pk):
    ver = get_object_or_404(VerificacionEficacia, pk=pk, eliminado=False)
    puede_gestionar = request.user.es_calidad or request.user.is_superuser
    form = VerificacionForm(instance=ver)

    if request.method == 'POST' and puede_gestionar:
        form = VerificacionForm(request.POST, request.FILES, instance=ver)
        if form.is_valid():
            v = form.save(commit=False)
            v.actualizado_por = request.user

            # Si pasa a No Eficaz, guardamos la fecha
            if v.estado == EstadoVerificacion.NO_EFICAZ and not v.fecha_realizada:
                v.fecha_realizada = timezone.now().date()

            v.save()
            messages.success(request, 'Verificación actualizada.')
            return redirect('verificacion:detalle', pk=pk)

    return render(request, 'verificacion/detalle.html', {
        'ver': ver,
        'form': form,
        'color_estado': COLORES_ESTADO.get(ver.estado, ''),
        'puede_gestionar': puede_gestionar,
    })

