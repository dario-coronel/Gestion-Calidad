from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from apps.nc.models import EstadoNC, NoConformidad
from apps.om.models import EficaciaOM, OportunidadMejora
from apps.proyectos.models import EstadoProyecto, Proyecto
from apps.qr.models import EstadoQR, QuejaReclamo
from apps.verificacion.models import EstadoVerificacion, VerificacionEficacia


@login_required
def lista(request):
    nc_qs = NoConformidad.objects.filter(eliminado=False).select_related('sector')
    qr_qs = QuejaReclamo.objects.filter(eliminado=False).select_related('sector')
    om_qs = OportunidadMejora.objects.filter(eliminado=False).select_related('sector')
    proyectos_qs = Proyecto.objects.filter(eliminado=False).select_related('sector')
    ver_qs = VerificacionEficacia.objects.filter(eliminado=False).select_related('proyecto')

    context = {
        'kpi_nc_abiertas': nc_qs.exclude(estado__in=[EstadoNC.CERRADA, EstadoNC.RECHAZADA]).count(),
        'kpi_qr_abiertas': qr_qs.exclude(estado__in=[EstadoQR.CERRADO, EstadoQR.RECHAZADO]).count(),
        'kpi_om_activas': om_qs.exclude(estado__in=['cerrada', 'rechazada']).count(),
        'kpi_proyectos_activos': proyectos_qs.exclude(estado=EstadoProyecto.FINALIZADO).count(),
        'kpi_verificaciones_pendientes': ver_qs.filter(estado__in=[EstadoVerificacion.PENDIENTE, EstadoVerificacion.EN_REVISION]).count(),
        'ultimas_nc': nc_qs.order_by('-fecha')[:5],
        'ultimas_qr': qr_qs.order_by('-fecha')[:5],
        'ultimas_om': om_qs.order_by('-fecha')[:5],
        'proyectos_recientes': proyectos_qs.order_by('-fecha_inicio')[:5],
        'verificaciones_recientes': ver_qs.order_by('-fecha_objetivo')[:5],
        'nc_por_sector': nc_qs.values('sector__nombre').annotate(total=Count('id')).order_by('-total', 'sector__nombre')[:8],
        'proyectos_no_eficaces': ver_qs.filter(estado=EstadoVerificacion.NO_EFICAZ).order_by('-actualizado_en')[:5],
        'oms_no_eficaces': om_qs.filter(eficacia=EficaciaOM.NO_EFICAZ).order_by('-actualizado_en')[:5],
    }
    return render(request, 'reportes/lista.html', context)
