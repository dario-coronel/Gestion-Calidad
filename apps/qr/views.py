from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import QuejaReclamo, EstadoQR, TipoReclamoQR
from .forms import QuejaReclamoForm, AdjuntoQRForm
from apps.om.models import OportunidadMejora, EstadoOM


COLORES_ESTADO = {
    EstadoQR.BORRADOR:       'bg-gray-100 text-gray-700',
    EstadoQR.EN_REVISION:    'bg-warning/10 text-warning',
    EstadoQR.EN_SEGUIMIENTO: 'bg-blue-50 text-blue-700',
    EstadoQR.CERRADO:        'bg-success/10 text-success',
    EstadoQR.RECHAZADO:      'bg-danger/10 text-danger',
}


def _es_responsable_de_qr(user, qr):
    return bool(
        user.is_authenticated
        and qr.responsable_id
        and getattr(qr.responsable, 'usuario_id', None) == user.id
    )


def _puede_gestionar_tipos_reclamo(user):
    return bool(
        user.is_authenticated and (
            getattr(user, 'es_admin', False)
            or user.is_superuser
            or user.has_perm('qr.change_tiporeclamoqr')
        )
    )


@login_required
def lista(request):
    qs = QuejaReclamo.objects.filter(eliminado=False).select_related(
        'responsable', 'sector', 'nc_relacionada', 'om_asociada'
    )

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
    puede_cargar = request.user.has_perm('qr.add_quejareclamo')
    if not puede_cargar:
        messages.error(request, 'No tenés permisos para cargar Quejas/Reclamos.')
        return redirect('qr:lista')

    if request.method == 'POST':
        form = QuejaReclamoForm(request.POST)
        adjunto_form = AdjuntoQRForm(request.POST, request.FILES)
        if form.is_valid():
            qr = form.save(commit=False)
            if not request.user.has_perm('qr.change_quejareclamo'):
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
    qr = get_object_or_404(
        QuejaReclamo.objects.select_related('nc_relacionada', 'om_asociada', 'responsable', 'sector'),
        pk=pk,
        eliminado=False,
    )
    puede_gestionar = request.user.has_perm('qr.change_quejareclamo')
    puede_editar = (
        puede_gestionar
        or (request.user.has_perm('qr.add_quejareclamo') and _es_responsable_de_qr(request.user, qr) and qr.estado == EstadoQR.BORRADOR)
    )

    if request.method == 'POST' and puede_gestionar:
        accion = request.POST.get('accion')

        if accion == 'cambiar_estado':
            nuevo_estado = request.POST.get('nuevo_estado')
            if nuevo_estado in dict(EstadoQR.choices):
                qr.estado = nuevo_estado
                if nuevo_estado == EstadoQR.CERRADO and not qr.fecha_cierre:
                    qr.fecha_cierre = timezone.now().date()
                qr.actualizado_por = request.user
                qr.save(update_fields=['estado', 'fecha_cierre', 'actualizado_por', 'actualizado_en'])
                messages.success(request, f'Estado actualizado a: {qr.get_estado_display()}')
                return redirect('qr:detalle', pk=pk)

        elif accion == 'revision_calidad':
            decision = request.POST.get('decision')
            if decision == 'aprobar':
                qr.estado = EstadoQR.EN_SEGUIMIENTO
                nueva_om = None
                if not qr.om_asociada_id:
                    nueva_om = OportunidadMejora.objects.create(
                        fecha=timezone.now().date(),
                        sector=qr.sector,
                        responsable=qr.responsable,
                        descripcion=f'OM derivada de {qr.folio}: {qr.descripcion}',
                        problema_a_mejorar=qr.descripcion,
                        beneficio_potencial=qr.prioridad,
                        clasificacion=qr.clasificacion or 'Calidad',
                        estado=EstadoOM.IMPLEMENTADA,
                        creado_por=request.user,
                        actualizado_por=request.user,
                    )
                    qr.om_asociada = nueva_om
                msg = 'Reclamo aceptado por Calidad y pasado a seguimiento.'
                if nueva_om:
                    msg += f' Se creó la OM {nueva_om.folio} asociada al reclamo.'
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
                qr.save(update_fields=['estado', 'om_asociada', 'actualizado_por', 'actualizado_en'])
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
        request.user.has_perm('qr.change_quejareclamo')
        or (request.user.has_perm('qr.add_quejareclamo') and _es_responsable_de_qr(request.user, qr) and qr.estado == EstadoQR.BORRADOR)
    )
    if not puede_editar:
        messages.error(request, 'No tenés permisos para editar este reclamo.')
        return redirect('qr:detalle', pk=pk)

    if request.method == 'POST':
        form = QuejaReclamoForm(request.POST, instance=qr)
        if form.is_valid():
            qr = form.save(commit=False)
            if not request.user.has_perm('qr.change_quejareclamo'):
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


@login_required
def tipos_reclamo_lista(request):
    if not _puede_gestionar_tipos_reclamo(request.user):
        messages.error(request, 'Solo el administrador puede gestionar tipos de reclamo.')
        return redirect('dashboard:index')
    tipos = TipoReclamoQR.objects.all()
    return render(request, 'qr/tipos_reclamo/lista.html', {'tipos': tipos})


@login_required
def tipo_reclamo_crear(request):
    if not _puede_gestionar_tipos_reclamo(request.user):
        messages.error(request, 'Solo el administrador puede gestionar tipos de reclamo.')
        return redirect('qr:tipos_reclamo_lista')

    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().lower()
        nombre = request.POST.get('nombre', '').strip()
        activo = request.POST.get('activo') == 'on'
        requiere_lote = request.POST.get('requiere_lote') == 'on'

        if not codigo or not nombre:
            messages.error(request, 'Código y nombre son obligatorios.')
        elif TipoReclamoQR.objects.filter(codigo__iexact=codigo).exists():
            messages.error(request, f'Ya existe un tipo con código "{codigo}".')
        elif TipoReclamoQR.objects.filter(nombre__iexact=nombre).exists():
            messages.error(request, f'Ya existe un tipo con nombre "{nombre}".')
        else:
            TipoReclamoQR.objects.create(
                codigo=codigo,
                nombre=nombre,
                activo=activo,
                requiere_lote=requiere_lote,
            )
            messages.success(request, f'Tipo de reclamo "{nombre}" creado.')
            return redirect('qr:tipos_reclamo_lista')

    return render(request, 'qr/tipos_reclamo/form.html', {
        'titulo': 'Nuevo Tipo de Reclamo',
        'accion': 'Crear',
    })


@login_required
def tipo_reclamo_editar(request, pk):
    if not _puede_gestionar_tipos_reclamo(request.user):
        messages.error(request, 'Solo el administrador puede gestionar tipos de reclamo.')
        return redirect('qr:tipos_reclamo_lista')

    tipo = get_object_or_404(TipoReclamoQR, pk=pk)
    uso_count = QuejaReclamo.objects.filter(eliminado=False, tipo_reclamo=tipo.codigo).count()

    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().lower()
        nombre = request.POST.get('nombre', '').strip()
        activo = request.POST.get('activo') == 'on'
        requiere_lote = request.POST.get('requiere_lote') == 'on'

        if not codigo or not nombre:
            messages.error(request, 'Código y nombre son obligatorios.')
        elif uso_count > 0 and codigo != tipo.codigo:
            messages.error(
                request,
                f'No se puede cambiar el código porque este tipo está en uso en {uso_count} QyR. Podés editar nombre, estado activo y requisito de lote.'
            )
        elif TipoReclamoQR.objects.filter(codigo__iexact=codigo).exclude(pk=tipo.pk).exists():
            messages.error(request, f'Ya existe otro tipo con código "{codigo}".')
        elif TipoReclamoQR.objects.filter(nombre__iexact=nombre).exclude(pk=tipo.pk).exists():
            messages.error(request, f'Ya existe otro tipo con nombre "{nombre}".')
        else:
            tipo.codigo = codigo
            tipo.nombre = nombre
            tipo.activo = activo
            tipo.requiere_lote = requiere_lote
            tipo.save()
            messages.success(request, f'Tipo de reclamo "{nombre}" actualizado.')
            return redirect('qr:tipos_reclamo_lista')

    return render(request, 'qr/tipos_reclamo/form.html', {
        'titulo': f'Editar Tipo: {tipo.nombre}',
        'accion': 'Guardar cambios',
        'tipo': tipo,
        'uso_count': uso_count,
    })


@login_required
def tipo_reclamo_eliminar(request, pk):
    if not _puede_gestionar_tipos_reclamo(request.user):
        messages.error(request, 'Solo el administrador puede gestionar tipos de reclamo.')
        return redirect('qr:tipos_reclamo_lista')

    tipo = get_object_or_404(TipoReclamoQR, pk=pk)
    uso_count = QuejaReclamo.objects.filter(eliminado=False, tipo_reclamo=tipo.codigo).count()

    if request.method == 'POST':
        if uso_count > 0:
            messages.error(
                request,
                f'No se puede eliminar "{tipo.nombre}" porque está en uso en {uso_count} QyR. Desactivalo desde edición.'
            )
            return redirect('qr:tipo_reclamo_editar', pk=tipo.pk)
        nombre = tipo.nombre
        tipo.delete()
        messages.success(request, f'Tipo de reclamo "{nombre}" eliminado.')
        return redirect('qr:tipos_reclamo_lista')

    return render(request, 'qr/tipos_reclamo/confirmar_eliminar.html', {
        'tipo': tipo,
        'uso_count': uso_count,
    })


# ── PDF ───────────────────────────────────────────────────────────────────────

@login_required
def pdf(request, pk):
    """Exporta el registro completo de la QyR en PDF."""
    qr = get_object_or_404(QuejaReclamo, pk=pk, eliminado=False)
    try:
        from weasyprint import HTML as WP_HTML
        html_string = render_to_string('qr/pdf.html', {'qr': qr}, request=request)
        pdf_bytes = WP_HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{qr.folio}.pdf"'
        return response
    except Exception as exc:
        messages.error(request, f'Error al generar PDF: {exc}')
        return redirect('qr:detalle', pk=pk)

