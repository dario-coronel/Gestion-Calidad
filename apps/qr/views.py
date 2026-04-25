from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import QuejaReclamo, EstadoQR
from .forms import QuejaReclamoForm, AdjuntoQRForm


COLORES_ESTADO = {
    EstadoQR.BORRADOR:       'bg-gray-100 text-gray-700',
    EstadoQR.EN_REVISION:    'bg-warning/10 text-warning',
    EstadoQR.EN_SEGUIMIENTO: 'bg-blue-50 text-blue-700',
    EstadoQR.CERRADO:        'bg-success/10 text-success',
    EstadoQR.RECHAZADO:      'bg-danger/10 text-danger',
}


@login_required
def lista(request):
    qs = QuejaReclamo.objects.filter(eliminado=False).select_related('responsable')

    estado = request.GET.get('estado', '')
    prioridad = request.GET.get('prioridad', '')
    q = request.GET.get('q', '')

    if estado:
        qs = qs.filter(estado=estado)
    if prioridad:
        qs = qs.filter(prioridad=prioridad)
    if q:
        qs = qs.filter(folio__icontains=q) | qs.filter(id_cliente_pedido__icontains=q)

    context = {
        'qr_list': qs,
        'colores_estado': COLORES_ESTADO,
        'estados': EstadoQR.choices,
        'filtros': {'estado': estado, 'prioridad': prioridad, 'q': q},
    }
    if request.htmx:
        return render(request, 'qr/partials/tabla_qr.html', context)
    return render(request, 'qr/lista.html', context)


@login_required
def crear(request):
    puede_cargar = request.user.es_operario or request.user.es_calidad or request.user.is_superuser
    if not puede_cargar:
        messages.error(request, 'No tenés permisos para cargar Quejas/Reclamos.')
        return redirect('qr:lista')

    if request.method == 'POST':
        form = QuejaReclamoForm(request.POST)
        adjunto_form = AdjuntoQRForm(request.POST, request.FILES)
        if form.is_valid():
            qr = form.save(commit=False)
            if request.user.es_operario:
                qr.estado = EstadoQR.EN_REVISION
            qr.creado_por = request.user
            qr.actualizado_por = request.user
            qr.save()
            if adjunto_form.is_valid() and request.FILES.get('archivo'):
                adj = adjunto_form.save(commit=False)
                adj.qr = qr
                adj.nombre = request.FILES['archivo'].name
                adj.subido_por = request.user
                adj.save()
            messages.success(request, f'{qr.folio} registrado correctamente.')
            return redirect('qr:detalle', pk=qr.pk)
    else:
        form = QuejaReclamoForm(initial={'fecha': timezone.now().date()})
        adjunto_form = AdjuntoQRForm()

    return render(request, 'qr/form.html', {
        'form': form,
        'adjunto_form': adjunto_form,
        'titulo': 'Nuevo Reclamo',
        'accion': 'Registrar',
    })


@login_required
def detalle(request, pk):
    qr = get_object_or_404(QuejaReclamo, pk=pk, eliminado=False)
    puede_gestionar = request.user.es_calidad or request.user.is_superuser
    puede_editar = (
        puede_gestionar
        or (request.user.es_operario and qr.responsable_id == request.user.id and qr.estado == EstadoQR.BORRADOR)
    )

    if request.method == 'POST' and puede_gestionar:
        accion = request.POST.get('accion')

        if accion == 'cambiar_estado':
            nuevo_estado = request.POST.get('nuevo_estado')
            if nuevo_estado in dict(EstadoQR.choices):
                qr.estado = nuevo_estado
                qr.actualizado_por = request.user
                qr.save(update_fields=['estado', 'actualizado_por', 'actualizado_en'])
                messages.success(request, f'Estado actualizado a: {qr.get_estado_display()}')
                return redirect('qr:detalle', pk=pk)

        elif accion == 'revision_calidad':
            decision = request.POST.get('decision')
            if decision == 'aprobar':
                qr.estado = EstadoQR.EN_SEGUIMIENTO
                msg = 'Reclamo aceptado por Calidad y pasado a seguimiento.'
            elif decision == 'rechazar':
                qr.estado = EstadoQR.RECHAZADO
                msg = 'Reclamo rechazado por Calidad.'
            elif decision == 'reenviar':
                qr.estado = EstadoQR.BORRADOR
                msg = 'Reclamo reenviado al operario por datos faltantes.'
            else:
                msg = ''

            if msg:
                qr.actualizado_por = request.user
                qr.save(update_fields=['estado', 'actualizado_por', 'actualizado_en'])
                messages.success(request, msg)
                return redirect('qr:detalle', pk=pk)

    return render(request, 'qr/detalle.html', {
        'qr': qr,
        'color_estado': COLORES_ESTADO.get(qr.estado, ''),
        'estados': EstadoQR.choices,
        'puede_gestionar': puede_gestionar,
        'puede_editar': puede_editar,
    })


@login_required
def editar(request, pk):
    qr = get_object_or_404(QuejaReclamo, pk=pk, eliminado=False)
    puede_editar = (
        request.user.es_calidad
        or request.user.is_superuser
        or (request.user.es_operario and qr.responsable_id == request.user.id and qr.estado == EstadoQR.BORRADOR)
    )
    if not puede_editar:
        messages.error(request, 'No tenés permisos para editar este reclamo.')
        return redirect('qr:detalle', pk=pk)

    if request.method == 'POST':
        form = QuejaReclamoForm(request.POST, instance=qr)
        if form.is_valid():
            qr = form.save(commit=False)
            if request.user.es_operario:
                qr.estado = EstadoQR.EN_REVISION
            qr.actualizado_por = request.user
            qr.save()
            messages.success(request, f'{qr.folio} actualizado.')
            return redirect('qr:detalle', pk=pk)
    else:
        form = QuejaReclamoForm(instance=qr)
    return render(request, 'qr/form.html', {
        'form': form,
        'adjunto_form': AdjuntoQRForm(),
        'titulo': f'Editar {qr.folio}',
        'accion': 'Guardar cambios',
        'qr': qr,
    })

