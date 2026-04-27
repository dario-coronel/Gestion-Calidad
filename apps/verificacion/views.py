from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import VerificacionEficacia, EstadoVerificacion
from .forms import VerificacionForm
from apps.nc.models import CincoPorques, EficaciaNC, EstadoNC, NoConformidad, OrigenNC


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
    puede_gestionar = request.user.has_perm('verificacion.change_verificacioneficacia')
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

            if v.estado == EstadoVerificacion.NO_EFICAZ and not v.nc_generada_id:
                proyecto = v.proyecto
                nueva_nc = NoConformidad.objects.create(
                    fecha=timezone.now().date(),
                    sector=proyecto.sector,
                    responsable=proyecto.responsable,
                    descripcion=(
                        f'Verificación no eficaz del proyecto {proyecto.folio}: {proyecto.nombre}. '
                        f'Resultado: {v.resultado_descripcion or "Sin detalle adicional."}'
                    ),
                    prioridad=proyecto.prioridad,
                    clasificacion='proceso',
                    estado=EstadoNC.BORRADOR,
                    origen=(OrigenNC.OM if proyecto.om_id else OrigenNC.DIRECTO),
                    om_relacionada=proyecto.om,
                    nc_origen=proyecto.nc,
                    eficacia=EficaciaNC.PENDIENTE,
                    creado_por=request.user,
                    actualizado_por=request.user,
                )
                CincoPorques.objects.create(nc=nueva_nc, etapa_1=nueva_nc.descripcion)
                v.nc_generada = nueva_nc
                v.save(update_fields=['nc_generada', 'actualizado_por', 'actualizado_en'])
                messages.warning(request, f'Verificación no eficaz. Se generó automáticamente la NC {nueva_nc.folio}.')
                return redirect('verificacion:detalle', pk=pk)

            messages.success(request, 'Verificación actualizada.')
            return redirect('verificacion:detalle', pk=pk)

    return render(request, 'verificacion/detalle.html', {
        'ver': ver,
        'form': form,
        'color_estado': COLORES_ESTADO.get(ver.estado, ''),
        'puede_gestionar': puede_gestionar,
    })

