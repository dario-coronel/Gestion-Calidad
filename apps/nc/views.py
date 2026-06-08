from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import (
    NoConformidad, CincoPorques, EstadoNC, EficaciaNC,
    CausaRaizIdentificada, NormaNC, PuntoNormaNC,
)
from .forms import NoConformidadForm, CincoPorquesForm, MatrizRiesgoForm, AdjuntoNCForm, EficaciaForm
from apps.core.models import Sector


# ── helpers ──────────────────────────────────────────────────────────────────

COLORES_ESTADO = {
    EstadoNC.BORRADOR:          'bg-gray-100 text-gray-700',
    EstadoNC.EN_REVISION:       'bg-warning/10 text-warning',
    EstadoNC.APROBADA:          'bg-primary/10 text-primary',
    EstadoNC.EN_IMPLEMENTACION: 'bg-blue-50 text-blue-700',
    EstadoNC.CERRADA:           'bg-success/10 text-success',
    EstadoNC.RECHAZADA:         'bg-danger/10 text-danger',
}


def _color_riesgo(valor):
    if not valor:
        return ''
    if valor >= 15:
        return 'text-danger font-bold'
    if valor >= 8:
        return 'text-warning font-semibold'
    return 'text-success'


def _es_admin_sistema(user):
    return user.is_authenticated and (getattr(user, 'es_admin', False) or user.is_superuser or user.is_staff)


def _puede_gestionar_nc(user):
    return user.has_perm('nc.change_noconformidad') or _es_admin_sistema(user)


def _es_responsable_de_nc(user, nc):
    return bool(
        user.is_authenticated
        and nc.responsable_id
        and getattr(nc.responsable, 'usuario_id', None) == user.id
    )


# ── lista ─────────────────────────────────────────────────────────────────────

@login_required
def lista(request):
    qs = NoConformidad.objects.filter(eliminado=False).select_related('responsable')

    # Filtros
    estado = request.GET.get('estado', '')
    prioridad = request.GET.get('prioridad', '')
    sector = request.GET.get('sector', '')
    q = request.GET.get('q', '')

    if estado:
        qs = qs.filter(estado=estado)
    if prioridad:
        qs = qs.filter(prioridad=prioridad)
    if sector:
        qs = qs.filter(sector_id=sector)
    if q:
        qs = qs.filter(folio__icontains=q) | qs.filter(descripcion__icontains=q)

    context = {
        'nc_list': qs,
        'colores_estado': COLORES_ESTADO,
        'estados': EstadoNC.choices,
        'prioridades': NoConformidad._meta.get_field('prioridad').choices,
        'sectores': Sector.objects.filter(activo=True).order_by('nombre'),
        'filtros': {'estado': estado, 'prioridad': prioridad, 'sector': sector, 'q': q},
    }

    # Respuesta parcial para HTMX
    if request.htmx:
        return render(request, 'nc/partials/tabla_nc.html', context)

    return render(request, 'nc/lista.html', context)


# ── crear ─────────────────────────────────────────────────────────────────────

@login_required
def crear(request):
    puede_cargar = request.user.has_perm('nc.add_noconformidad')
    if not puede_cargar:
        messages.error(request, 'No tenés permisos para cargar No Conformidades.')
        return redirect('nc:lista')

    if request.method == 'POST':
        form = NoConformidadForm(request.POST)
        adjunto_form = AdjuntoNCForm(request.POST, request.FILES)
        if form.is_valid():
            nc = form.save(commit=False)
            # Lo cargado por operario entra al circuito de revisión de Calidad.
            if not _puede_gestionar_nc(request.user):
                nc.estado = EstadoNC.EN_REVISION
            nc.creado_por = request.user
            nc.actualizado_por = request.user
            nc.save()
            # Crear 5 Porqués asociados con el 1er por qué en blanco.
            CincoPorques.objects.create(nc=nc)
            # Adjunto opcional
            if adjunto_form.is_valid() and request.FILES.get('archivo'):
                adj = adjunto_form.save(commit=False)
                adj.nc = nc
                adj.nombre = request.FILES['archivo'].name
                adj.subido_por = request.user
                adj.save()
            messages.success(request, f'No Conformidad {nc.folio} creada correctamente.')
            return redirect('nc:detalle', pk=nc.pk)
    else:
        form = NoConformidadForm(initial={'fecha': timezone.now().date()})
        adjunto_form = AdjuntoNCForm()

    return render(request, 'nc/form.html', {
        'form': form,
        'adjunto_form': adjunto_form,
        'titulo': 'Nueva No Conformidad',
        'accion': 'Registrar NC',
    })


# ── detalle ───────────────────────────────────────────────────────────────────

@login_required
def detalle(request, pk):
    nc = get_object_or_404(NoConformidad, pk=pk, eliminado=False)
    puede_calidad = _puede_gestionar_nc(request.user)
    puede_editar = (
        puede_calidad
        or (request.user.has_perm('nc.add_noconformidad') and _es_responsable_de_nc(request.user, nc) and nc.estado == EstadoNC.BORRADOR)
    )
    cinco_p = getattr(nc, 'cinco_porques', None)
    # Auto-crear 5 Porqués si no existe (NCs importadas, seed, migradas, etc.)
    if cinco_p is None and puede_editar:
        cinco_p = CincoPorques.objects.create(nc=nc)
    # Normaliza registros legacy: limpia etapa_1 si solo fue auto-copiada desde descripción.
    if (
        cinco_p
        and cinco_p.etapa_1 == nc.descripcion
        and not cinco_p.etapa_2
        and not cinco_p.etapa_3
        and not cinco_p.etapa_4
        and not cinco_p.etapa_5
        and not cinco_p.causa_raiz
        and not cinco_p.accion_correctiva
    ):
        cinco_p.etapa_1 = ''
        cinco_p.save(update_fields=['etapa_1', 'actualizado_en'])
    cinco_form = None
    matriz_form = None

    if request.method == 'POST':
        accion = request.POST.get('accion', '')

        # Guardar 5 Porqués (solo calidad/admin)
        if accion == 'guardar_5p' and cinco_p and puede_calidad:
            cinco_form = CincoPorquesForm(request.POST, instance=cinco_p)
            if cinco_form.is_valid():
                cp = cinco_form.save(commit=False)
                cp.completo = bool(cp.causa_raiz and cp.accion_correctiva)
                cp.save()
                nc.actualizado_por = request.user
                nc.save(update_fields=['actualizado_por', 'actualizado_en'])
                messages.success(request, 'Análisis 5 Porqués guardado.')
                return redirect('nc:detalle', pk=pk)

        # Guardar Matriz de Riesgo (solo calidad/admin)
        elif accion == 'guardar_riesgo' and puede_calidad:
            matriz_form = MatrizRiesgoForm(request.POST, instance=nc)
            if matriz_form.is_valid():
                matriz_form.save()
                messages.success(request, 'Matriz de riesgo actualizada.')
                return redirect('nc:detalle', pk=pk)

        # Cambio de estado (solo calidad/admin)
        elif accion == 'cambiar_estado' and puede_calidad:
            nuevo_estado = request.POST.get('nuevo_estado')
            if nuevo_estado in dict(EstadoNC.choices):
                nc.estado = nuevo_estado
                nc.actualizado_por = request.user
                nc.save(update_fields=['estado', 'actualizado_por', 'actualizado_en'])
                messages.success(request, f'Estado actualizado a: {nc.get_estado_display()}')
                return redirect('nc:detalle', pk=pk)

        # Flujo de revisión de calidad: aprobar / rechazar / reenviar al operario
        elif accion == 'revision_calidad' and puede_calidad:
            decision = request.POST.get('decision')
            if decision == 'aprobar':
                nc.estado = EstadoNC.APROBADA
                msg = 'NC aprobada por Calidad.'
            elif decision == 'rechazar':
                nc.estado = EstadoNC.RECHAZADA
                msg = 'NC rechazada por Calidad.'
            elif decision == 'reenviar':
                nc.estado = EstadoNC.BORRADOR
                msg = 'NC reenviada al operario para completar datos.'
            else:
                msg = ''

            if msg:
                nc.actualizado_por = request.user
                nc.save(update_fields=['estado', 'actualizado_por', 'actualizado_en'])
                messages.success(request, msg)
                return redirect('nc:detalle', pk=pk)

        # Evaluar eficacia de la acción correctiva (solo calidad/admin)
        elif accion == 'marcar_eficacia' and puede_calidad:
            eficacia_form = EficaciaForm(request.POST, instance=nc)
            if eficacia_form.is_valid():
                nc_guardada = eficacia_form.save(commit=False)
                nueva_eficacia = nc_guardada.eficacia

                if nueva_eficacia == EficaciaNC.NO_EFICAZ:
                    # Cerrar NC actual y abrir una nueva vinculada
                    nc_guardada.estado = EstadoNC.CERRADA
                    nc_guardada.actualizado_por = request.user
                    nc_guardada.save()
                    nueva_nc = NoConformidad.objects.create(
                        fecha=timezone.now().date(),
                        sector=nc.sector,
                        responsable=nc.responsable,
                        norma=nc.norma,
                        punto_norma=nc.punto_norma,
                        descripcion=f'Seguimiento de {nc.folio} (No Eficaz): {nc.descripcion}',
                        prioridad=nc.prioridad,
                        clasificacion=nc.clasificacion,
                        origen=nc.origen,
                        qr_relacionada=nc.qr_relacionada,
                        om_relacionada=nc.om_relacionada,
                        nc_origen=nc,
                        estado=EstadoNC.BORRADOR,
                        creado_por=request.user,
                        actualizado_por=request.user,
                    )
                    CincoPorques.objects.create(nc=nueva_nc)
                    messages.warning(
                        request,
                        f'NC marcada como No Eficaz. Se generó la nueva NC {nueva_nc.folio} para seguimiento.'
                    )
                    return redirect('nc:detalle', pk=nueva_nc.pk)
                else:
                    nc_guardada.actualizado_por = request.user
                    nc_guardada.save()
                    messages.success(request, f'Eficacia actualizada: {nc_guardada.get_eficacia_display()}')
                    return redirect('nc:detalle', pk=pk)

    # Mostrar form editable solo a calidad/admin
    eficacia_form = None
    if puede_calidad:
        if not cinco_form and cinco_p:
            cinco_form = CincoPorquesForm(instance=cinco_p)
    if puede_calidad:
        if not matriz_form:
            matriz_form = MatrizRiesgoForm(instance=nc)
        eficacia_form = EficaciaForm(instance=nc)

    etapas = [
        ('etapa_1', '¿Por qué? (1º nivel)'),
        ('etapa_2', '¿Por qué? (2º nivel)'),
        ('etapa_3', '¿Por qué? (3º nivel)'),
        ('etapa_4', '¿Por qué? (4º nivel)'),
        ('etapa_5', '¿Por qué? (5º nivel)'),
    ]

    qr_relacionada = None
    om_relacionada = None
    nc_origen_relacionada = None
    try:
        qr_relacionada = nc.qr_relacionada
    except (ObjectDoesNotExist, DatabaseError):
        qr_relacionada = None
    try:
        om_relacionada = nc.om_relacionada
    except (ObjectDoesNotExist, DatabaseError):
        om_relacionada = None
    try:
        nc_origen_relacionada = nc.nc_origen
    except (ObjectDoesNotExist, DatabaseError):
        nc_origen_relacionada = None

    return render(request, 'nc/detalle.html', {
        'nc': nc,
        'cinco_form': cinco_form,
        'matriz_form': matriz_form,
        'eficacia_form': eficacia_form,
        'cinco_p': cinco_p,
        'etapas': etapas,
        'color_estado': COLORES_ESTADO.get(nc.estado, ''),
        'color_riesgo': _color_riesgo(nc.riesgo_calculado),
        'estados': EstadoNC.choices,
        'puede_calidad': puede_calidad,
        'puede_editar_riesgo': puede_calidad,
        'puede_cambiar_estado': puede_calidad,
        'puede_editar': puede_editar,
        'qr_relacionada': qr_relacionada,
        'om_relacionada': om_relacionada,
        'nc_origen_relacionada': nc_origen_relacionada,
    })


# ── editar ────────────────────────────────────────────────────────────────────

@login_required
def editar(request, pk):
    nc = get_object_or_404(NoConformidad, pk=pk, eliminado=False)
    puede_editar = (
        _puede_gestionar_nc(request.user)
        or (request.user.has_perm('nc.add_noconformidad') and _es_responsable_de_nc(request.user, nc) and nc.estado == EstadoNC.BORRADOR)
    )
    if not puede_editar:
        messages.error(request, 'No tenés permisos para editar esta NC.')
        return redirect('nc:detalle', pk=pk)

    if request.method == 'POST':
        form = NoConformidadForm(request.POST, instance=nc)
        if form.is_valid():
            nc = form.save(commit=False)
            # Si el operario corrige una NC devuelta, vuelve a revisión.
            if not _puede_gestionar_nc(request.user):
                nc.estado = EstadoNC.EN_REVISION
            nc.actualizado_por = request.user
            nc.save()
            messages.success(request, f'{nc.folio} actualizada.')
            return redirect('nc:detalle', pk=pk)
    else:
        form = NoConformidadForm(instance=nc)

    return render(request, 'nc/form.html', {
        'form': form,
        'adjunto_form': AdjuntoNCForm(),
        'nc': nc,
        'titulo': f'Editar {nc.folio}',
        'accion': 'Guardar cambios',
    })


# ── PDF ───────────────────────────────────────────────────────────────────────

@login_required
def pdf_resumen(request, pk):
    """Exporta un resumen en PDF de una sola página (datos clave)."""
    nc = get_object_or_404(NoConformidad, pk=pk, eliminado=False)
    try:
        from weasyprint import HTML as WP_HTML
        html_string = render_to_string('nc/pdf_resumen.html', {
            'nc': nc,
            'color_riesgo': _color_riesgo(nc.riesgo_calculado),
        }, request=request)
        pdf_bytes = WP_HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{nc.folio}_resumen.pdf"'
        return response
    except Exception as exc:
        messages.error(request, f'Error al generar PDF: {exc}')
        return redirect('nc:detalle', pk=pk)


@login_required
def pdf_completo(request, pk):
    """Exporta el registro completo de la NC en PDF (todos los campos + 5 Porqués)."""
    nc = get_object_or_404(NoConformidad, pk=pk, eliminado=False)
    cinco_p = getattr(nc, 'cinco_porques', None)
    try:
        from weasyprint import HTML as WP_HTML
        html_string = render_to_string('nc/pdf_completo.html', {
            'nc': nc,
            'cinco_p': cinco_p,
            'color_riesgo': _color_riesgo(nc.riesgo_calculado),
        }, request=request)
        pdf_bytes = WP_HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{nc.folio}_completo.pdf"'
        return response
    except Exception as exc:
        messages.error(request, f'Error al generar PDF: {exc}')
        return redirect('nc:detalle', pk=pk)


# ── Causa Raíz Identificada CRUD ──────────────────────────────────────────────

def _puede_gestionar_causa_raiz(user):
    """Verifica si el usuario puede gestionar Causa Raíz Identificada (admin/calidad)."""
    if not user.is_authenticated:
        return False
    if user.es_admin or user.is_superuser or user.is_staff:
        return True
    from apps.accounts.models import Rol
    return user.rol == Rol.CALIDAD


def _puede_gestionar_normas(user):
    return _puede_gestionar_causa_raiz(user)


def _parsear_puntos_norma(raw_texto):
    puntos = []
    vistos = set()
    for linea in raw_texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        codigo = ''
        descripcion = linea
        if ' - ' in linea:
            codigo, descripcion = linea.split(' - ', 1)
        elif ':' in linea:
            codigo, descripcion = linea.split(':', 1)
        codigo = codigo.strip()
        descripcion = descripcion.strip()
        if not descripcion:
            continue
        clave = (codigo.lower(), descripcion.lower())
        if clave in vistos:
            continue
        vistos.add(clave)
        puntos.append({'codigo': codigo, 'descripcion': descripcion})
    return puntos


def _serializar_puntos_norma(normas):
    serializado = {}
    for norma in normas:
        serializado[str(norma.pk)] = [
            {
                'id': punto.pk,
                'label': f'{punto.codigo} - {punto.descripcion}' if punto.codigo else punto.descripcion,
            }
            for punto in norma.puntos.filter(activo=True, eliminado=False).order_by('codigo', 'descripcion')
        ]
    return serializado


@login_required
def puntos_norma_por_norma(request, norma_id):
    """Devuelve puntos activos de una norma para el dropdown dependiente."""
    if not request.user.is_authenticated:
        return JsonResponse({'results': []}, status=403)

    puntos = PuntoNormaNC.objects.filter(
        norma_id=norma_id,
        activo=True,
        eliminado=False,
        norma__eliminado=False,
        norma__activo=True,
    ).order_by('codigo', 'descripcion')

    return JsonResponse({
        'results': [
            {
                'id': punto.pk,
                'label': f'{punto.codigo} - {punto.descripcion}' if punto.codigo else punto.descripcion,
            }
            for punto in puntos
        ]
    })


@login_required
def causa_raiz_lista(request):
    """Lista de Causas Raíz Identificadas."""
    if not _puede_gestionar_causa_raiz(request.user):
        messages.error(request, 'No tienes permiso para acceder a este recurso.')
        return redirect('core:home')
    
    qs = CausaRaizIdentificada.objects.filter(eliminado=False).order_by('nombre')
    
    context = {
        'title': 'Causas Raíz Identificadas',
        'causas_raiz': qs,
        'total': qs.count(),
    }
    return render(request, 'nc/causa_raiz_lista.html', context)


@login_required
def causa_raiz_crear(request):
    """Crear nueva Causa Raíz Identificada."""
    if not _puede_gestionar_causa_raiz(request.user):
        messages.error(request, 'No tienes permiso para acceder a este recurso.')
        return redirect('core:home')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
            return render(request, 'nc/causa_raiz_form.html', {
                'title': 'Nueva Causa Raíz Identificada',
                'is_create': True,
            })
        
        # Verificar si ya existe
        if CausaRaizIdentificada.objects.filter(nombre__iexact=nombre, eliminado=False).exists():
            messages.error(request, f'Ya existe una Causa Raíz con el nombre "{nombre}".')
            return render(request, 'nc/causa_raiz_form.html', {
                'title': 'Nueva Causa Raíz Identificada',
                'is_create': True,
                'nombre': nombre,
                'descripcion': descripcion,
            })
        
        causa = CausaRaizIdentificada.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            creado_por=request.user,
            actualizado_por=request.user,
        )
        messages.success(request, f'Causa Raíz "{nombre}" creada exitosamente.')
        return redirect('nc:causa_raiz_detalle', pk=causa.pk)
    
    return render(request, 'nc/causa_raiz_form.html', {
        'title': 'Nueva Causa Raíz Identificada',
        'is_create': True,
    })


@login_required
def causa_raiz_detalle(request, pk):
    """Detalle de una Causa Raíz Identificada."""
    if not _puede_gestionar_causa_raiz(request.user):
        messages.error(request, 'No tienes permiso para acceder a este recurso.')
        return redirect('core:home')
    
    causa = get_object_or_404(CausaRaizIdentificada, pk=pk, eliminado=False)
    
    context = {
        'title': f'Causa Raíz: {causa.nombre}',
        'causa': causa,
    }
    return render(request, 'nc/causa_raiz_detalle.html', context)


@login_required
def causa_raiz_editar(request, pk):
    """Editar una Causa Raíz Identificada."""
    if not _puede_gestionar_causa_raiz(request.user):
        messages.error(request, 'No tienes permiso para acceder a este recurso.')
        return redirect('core:home')
    
    causa = get_object_or_404(CausaRaizIdentificada, pk=pk, eliminado=False)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
            return render(request, 'nc/causa_raiz_form.html', {
                'title': f'Editar Causa Raíz: {causa.nombre}',
                'causa': causa,
                'nombre': nombre,
                'descripcion': descripcion,
            })
        
        # Verificar si existe otro con el mismo nombre
        if CausaRaizIdentificada.objects.filter(
            nombre__iexact=nombre, eliminado=False
        ).exclude(pk=pk).exists():
            messages.error(request, f'Ya existe otra Causa Raíz con el nombre "{nombre}".')
            return render(request, 'nc/causa_raiz_form.html', {
                'title': f'Editar Causa Raíz: {causa.nombre}',
                'causa': causa,
                'nombre': nombre,
                'descripcion': descripcion,
            })
        
        causa.nombre = nombre
        causa.descripcion = descripcion
        causa.actualizado_por = request.user
        causa.save()
        
        messages.success(request, f'Causa Raíz "{nombre}" actualizada exitosamente.')
        return redirect('nc:causa_raiz_detalle', pk=causa.pk)
    
    context = {
        'title': f'Editar Causa Raíz: {causa.nombre}',
        'causa': causa,
        'nombre': causa.nombre,
        'descripcion': causa.descripcion,
    }
    return render(request, 'nc/causa_raiz_form.html', context)


@login_required
def causa_raiz_eliminar(request, pk):
    """Eliminar (lógico) una Causa Raíz Identificada."""
    if not _puede_gestionar_causa_raiz(request.user):
        messages.error(request, 'No tienes permiso para acceder a este recurso.')
        return redirect('core:home')
    
    causa = get_object_or_404(CausaRaizIdentificada, pk=pk, eliminado=False)
    
    if request.method == 'POST':
        nombre = causa.nombre
        causa.eliminado = True
        causa.actualizado_por = request.user
        causa.save()
        
        messages.success(request, f'Causa Raíz "{nombre}" eliminada exitosamente.')
        return redirect('nc:causa_raiz_lista')
    
    context = {
        'title': f'Eliminar Causa Raíz: {causa.nombre}',
        'causa': causa,
    }
    return render(request, 'nc/causa_raiz_confirmar_eliminar.html', context)


# ── Normas CRUD ───────────────────────────────────────────────────────────────


@login_required
def norma_lista(request):
    """Lista de normas y sus puntos asociados."""
    if not _puede_gestionar_normas(request.user):
        messages.error(request, 'No tienes permiso para acceder a este recurso.')
        return redirect('core:home')

    normas = NormaNC.objects.filter(eliminado=False).prefetch_related(
        'puntos'
    ).annotate(
        total_puntos_activos=Count('puntos', filter=Q(puntos__eliminado=False, puntos__activo=True))
    ).order_by('nombre')
    context = {
        'title': 'Normas',
        'normas': normas,
        'total': normas.count(),
    }
    return render(request, 'nc/norma_lista.html', context)


@login_required
def norma_crear(request):
    """Crear una norma."""
    if not _puede_gestionar_normas(request.user):
        messages.error(request, 'No tienes permiso para acceder a este recurso.')
        return redirect('core:home')

    if request.method == 'POST':
        from .forms import NormaNCForm
        form = NormaNCForm(request.POST)
        if form.is_valid():
            norma = form.save(commit=False)
            norma.creado_por = request.user
            norma.actualizado_por = request.user
            norma.save()
            messages.success(request, f'Norma "{norma.nombre}" creada exitosamente.')
            return redirect('nc:norma_detalle', pk=norma.pk)
    else:
        from .forms import NormaNCForm
        form = NormaNCForm()

    return render(request, 'nc/norma_form.html', {
        'title': 'Nueva Norma',
        'is_create': True,
        'form': form,
    })


@login_required
def norma_detalle(request, pk):
    """Detalle de una norma y sus puntos."""
    if not _puede_gestionar_normas(request.user):
        messages.error(request, 'No tienes permiso para acceder a este recurso.')
        return redirect('core:home')

    norma = get_object_or_404(
        NormaNC.objects.prefetch_related('puntos'),
        pk=pk,
        eliminado=False,
    )
    context = {
        'title': f'Norma: {norma.nombre}',
        'norma': norma,
        'puntos': norma.puntos.filter(eliminado=False, activo=True).order_by('codigo', 'descripcion'),
    }
    return render(request, 'nc/norma_detalle.html', context)


@login_required
def norma_editar(request, pk):
    """Editar una norma."""
    if not _puede_gestionar_normas(request.user):
        messages.error(request, 'No tienes permiso para acceder a este recurso.')
        return redirect('core:home')

    norma = get_object_or_404(NormaNC, pk=pk, eliminado=False)

    if request.method == 'POST':
        from .forms import NormaNCForm
        form = NormaNCForm(request.POST, instance=norma)
        if form.is_valid():
            norma = form.save(commit=False)
            norma.actualizado_por = request.user
            norma.save()
            messages.success(request, f'Norma "{norma.nombre}" actualizada exitosamente.')
            return redirect('nc:norma_detalle', pk=norma.pk)
    else:
        from .forms import NormaNCForm
        form = NormaNCForm(instance=norma)

    return render(request, 'nc/norma_form.html', {
        'title': f'Editar Norma: {norma.nombre}',
        'norma': norma,
        'form': form,
    })


@login_required
def norma_eliminar(request, pk):
    """Eliminar lógicamente una norma y sus puntos."""
    if not _puede_gestionar_normas(request.user):
        messages.error(request, 'No tienes permiso para acceder a este recurso.')
        return redirect('core:home')

    norma = get_object_or_404(NormaNC, pk=pk, eliminado=False)

    if request.method == 'POST':
        nombre = norma.nombre
        norma.eliminado = True
        norma.actualizado_por = request.user
        norma.save()
        norma.puntos.filter(eliminado=False).update(eliminado=True, actualizado_por=request.user)
        messages.success(request, f'Norma "{nombre}" eliminada exitosamente.')
        return redirect('nc:norma_lista')

    return render(request, 'nc/norma_confirmar_eliminar.html', {
        'title': f'Eliminar Norma: {norma.nombre}',
        'norma': norma,
    })


# ── Puntos de Norma CRUD ──────────────────────────────────────────────────────

@login_required
def punto_lista(request, norma_id=None):
    """Lista de puntos de una norma, o todas si no especifica norma."""
    if not _puede_gestionar_normas(request.user):
        messages.error(request, 'No tienes permiso para acceder a este recurso.')
        return redirect('core:home')

    norma = None
    if norma_id:
        norma = get_object_or_404(NormaNC, pk=norma_id, eliminado=False)
        puntos = norma.puntos.filter(eliminado=False).order_by('codigo', 'descripcion')
    else:
        puntos = PuntoNormaNC.objects.filter(eliminado=False).select_related('norma').order_by('norma__nombre', 'codigo', 'descripcion')

    context = {
        'title': f'Puntos de {norma.nombre}' if norma else 'Puntos de Normas',
        'norma': norma,
        'puntos': puntos,
        'normas': NormaNC.objects.filter(eliminado=False, activo=True).order_by('nombre'),
    }
    return render(request, 'nc/punto_lista.html', context)


@login_required
def punto_crear(request, norma_id):
    """Crear un punto de norma."""
    if not _puede_gestionar_normas(request.user):
        messages.error(request, 'No tienes permiso para acceder a este recurso.')
        return redirect('core:home')

    norma = get_object_or_404(NormaNC, pk=norma_id, eliminado=False)

    if request.method == 'POST':
        from .forms import PuntoNormaNCForm
        form = PuntoNormaNCForm(request.POST)
        if form.is_valid():
            codigo = (form.cleaned_data.get('codigo') or '').strip()
            descripcion = (form.cleaned_data.get('descripcion') or '').strip()
            activo = form.cleaned_data.get('activo', True)

            existente = PuntoNormaNC.objects.filter(
                norma=norma,
                codigo=codigo,
                descripcion=descripcion,
            ).first()

            if existente and not existente.eliminado:
                form.add_error('descripcion', 'Ya existe un punto con ese código y descripción para esta norma.')
            elif existente and existente.eliminado:
                existente.eliminado = False
                existente.activo = activo
                existente.actualizado_por = request.user
                existente.save(update_fields=['eliminado', 'activo', 'actualizado_por', 'actualizado_en'])
                messages.success(request, 'El punto ya existía y fue reactivado exitosamente.')
                return redirect('nc:punto_lista_norma', norma_id=norma.pk)
            else:
                punto = form.save(commit=False)
                punto.norma = norma
                punto.creado_por = request.user
                punto.actualizado_por = request.user
                punto.save()
                messages.success(request, 'Punto creado exitosamente.')
                return redirect('nc:punto_lista_norma', norma_id=norma.pk)
    else:
        from .forms import PuntoNormaNCForm
        form = PuntoNormaNCForm()

    return render(request, 'nc/punto_form.html', {
        'title': f'Nuevo Punto - {norma.nombre}',
        'norma': norma,
        'form': form,
        'is_create': True,
    })


@login_required
def punto_editar(request, pk):
    """Editar un punto de norma."""
    if not _puede_gestionar_normas(request.user):
        messages.error(request, 'No tienes permiso para acceder a este recurso.')
        return redirect('core:home')

    punto = get_object_or_404(PuntoNormaNC, pk=pk, eliminado=False)

    if request.method == 'POST':
        from .forms import PuntoNormaNCForm
        form = PuntoNormaNCForm(request.POST, instance=punto)
        if form.is_valid():
            codigo = (form.cleaned_data.get('codigo') or '').strip()
            descripcion = (form.cleaned_data.get('descripcion') or '').strip()

            conflicto = PuntoNormaNC.objects.filter(
                norma=punto.norma,
                codigo=codigo,
                descripcion=descripcion,
                eliminado=False,
            ).exclude(pk=punto.pk).exists()

            if conflicto:
                form.add_error('descripcion', 'Ya existe otro punto activo con ese código y descripción para esta norma.')
            else:
                punto = form.save(commit=False)
                punto.actualizado_por = request.user
                punto.save()
                messages.success(request, 'Punto actualizado exitosamente.')
                return redirect('nc:punto_lista_norma', norma_id=punto.norma.pk)
    else:
        from .forms import PuntoNormaNCForm
        form = PuntoNormaNCForm(instance=punto)

    return render(request, 'nc/punto_form.html', {
        'title': f'Editar Punto - {punto.norma.nombre}',
        'norma': punto.norma,
        'punto': punto,
        'form': form,
    })


@login_required
def punto_eliminar(request, pk):
    """Eliminar un punto de norma."""
    if not _puede_gestionar_normas(request.user):
        messages.error(request, 'No tienes permiso para acceder a este recurso.')
        return redirect('core:home')

    punto = get_object_or_404(PuntoNormaNC, pk=pk, eliminado=False)
    norma_id = punto.norma.pk

    if request.method == 'POST':
        punto.eliminado = True
        punto.actualizado_por = request.user
        punto.save()
        messages.success(request, 'Punto eliminado exitosamente.')
        return redirect('nc:punto_lista_norma', norma_id=norma_id)

    return render(request, 'nc/punto_confirmar_eliminar.html', {
        'title': f'Eliminar Punto - {punto.norma.nombre}',
        'punto': punto,
        'norma': punto.norma,
    })
