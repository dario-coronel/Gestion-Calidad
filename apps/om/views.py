from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import OportunidadMejora, EstadoOM
from .forms import OportunidadMejoraForm, AdjuntoOMForm


COLORES_ESTADO = {
    EstadoOM.BORRADOR:          'bg-gray-100 text-gray-700',
    EstadoOM.EN_REVISION:       'bg-warning/10 text-warning',
    EstadoOM.APROBADA:          'bg-primary/10 text-primary',
    EstadoOM.EN_IMPLEMENTACION: 'bg-blue-50 text-blue-700',
    EstadoOM.CERRADA:           'bg-success/10 text-success',
    EstadoOM.RECHAZADA:         'bg-danger/10 text-danger',
}


@login_required
def lista(request):
    qs = OportunidadMejora.objects.filter(eliminado=False).select_related('responsable')

    estado = request.GET.get('estado', '')
    q = request.GET.get('q', '')

    if estado:
        qs = qs.filter(estado=estado)
    if q:
        qs = qs.filter(folio__icontains=q) | qs.filter(descripcion__icontains=q)

    context = {
        'om_list': qs,
        'colores_estado': COLORES_ESTADO,
        'estados': EstadoOM.choices,
        'filtros': {'estado': estado, 'q': q},
    }
    if request.htmx:
        return render(request, 'om/partials/tabla_om.html', context)
    return render(request, 'om/lista.html', context)


@login_required
def crear(request):
    puede_cargar = request.user.es_operario or request.user.es_calidad or request.user.is_superuser
    if not puede_cargar:
        messages.error(request, 'No tenés permisos para cargar Oportunidades de Mejora.')
        return redirect('om:lista')

    if request.method == 'POST':
        form = OportunidadMejoraForm(request.POST)
        adjunto_form = AdjuntoOMForm(request.POST, request.FILES)
        if form.is_valid():
            om = form.save(commit=False)
            if request.user.es_operario:
                om.estado = EstadoOM.EN_REVISION
            om.creado_por = request.user
            om.actualizado_por = request.user
            om.save()
            if adjunto_form.is_valid() and request.FILES.get('archivo'):
                adj = adjunto_form.save(commit=False)
                adj.om = om
                adj.nombre = request.FILES['archivo'].name
                adj.subido_por = request.user
                adj.save()
            messages.success(request, f'{om.folio} registrada correctamente.')
            return redirect('om:detalle', pk=om.pk)
    else:
        form = OportunidadMejoraForm(initial={'fecha': timezone.now().date()})
        adjunto_form = AdjuntoOMForm()

    return render(request, 'om/form.html', {
        'form': form,
        'adjunto_form': adjunto_form,
        'titulo': 'Nueva Oportunidad de Mejora',
        'accion': 'Registrar OM',
    })


@login_required
def detalle(request, pk):
    om = get_object_or_404(OportunidadMejora, pk=pk, eliminado=False)
    puede_gestionar = request.user.es_calidad or request.user.is_superuser
    puede_editar = (
        puede_gestionar
        or (request.user.es_operario and om.responsable_id == request.user.id and om.estado == EstadoOM.BORRADOR)
    )

    if request.method == 'POST' and puede_gestionar:
        accion = request.POST.get('accion')

        if accion == 'cambiar_estado':
            nuevo_estado = request.POST.get('nuevo_estado')
            if nuevo_estado in dict(EstadoOM.choices):
                om.estado = nuevo_estado
                om.actualizado_por = request.user
                om.save(update_fields=['estado', 'actualizado_por', 'actualizado_en'])
                messages.success(request, f'Estado actualizado a: {om.get_estado_display()}')
                return redirect('om:detalle', pk=pk)

        elif accion == 'revision_calidad':
            decision = request.POST.get('decision')
            if decision == 'aprobar':
                om.estado = EstadoOM.APROBADA
                msg = 'OM aprobada por Calidad.'
            elif decision == 'rechazar':
                om.estado = EstadoOM.RECHAZADA
                msg = 'OM rechazada por Calidad.'
            elif decision == 'reenviar':
                om.estado = EstadoOM.BORRADOR
                msg = 'OM reenviada al operario por datos faltantes.'
            else:
                msg = ''

            if msg:
                om.actualizado_por = request.user
                om.save(update_fields=['estado', 'actualizado_por', 'actualizado_en'])
                messages.success(request, msg)
                return redirect('om:detalle', pk=pk)

    return render(request, 'om/detalle.html', {
        'om': om,
        'color_estado': COLORES_ESTADO.get(om.estado, ''),
        'estados': EstadoOM.choices,
        'puede_gestionar': puede_gestionar,
        'puede_editar': puede_editar,
    })


@login_required
def editar(request, pk):
    om = get_object_or_404(OportunidadMejora, pk=pk, eliminado=False)
    puede_editar = (
        request.user.es_calidad
        or request.user.is_superuser
        or (request.user.es_operario and om.responsable_id == request.user.id and om.estado == EstadoOM.BORRADOR)
    )
    if not puede_editar:
        messages.error(request, 'No tenés permisos para editar esta OM.')
        return redirect('om:detalle', pk=pk)

    if request.method == 'POST':
        form = OportunidadMejoraForm(request.POST, instance=om)
        if form.is_valid():
            om = form.save(commit=False)
            if request.user.es_operario:
                om.estado = EstadoOM.EN_REVISION
            om.actualizado_por = request.user
            om.save()
            messages.success(request, f'{om.folio} actualizada.')
            return redirect('om:detalle', pk=pk)
    else:
        form = OportunidadMejoraForm(instance=om)
    return render(request, 'om/form.html', {
        'form': form,
        'adjunto_form': AdjuntoOMForm(),
        'titulo': f'Editar {om.folio}',
        'accion': 'Guardar cambios',
        'om': om,
    })

