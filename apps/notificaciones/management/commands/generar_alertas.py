"""
Management command: generar_alertas
Detecta condiciones de alerta y crea notificaciones.
Debe ejecutarse periódicamente (ej. diariamente con cron o Celery beat).

Uso: python manage.py generar_alertas
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.urls import reverse


class Command(BaseCommand):
    help = 'Genera notificaciones automáticas por vencimientos y alertas del sistema'

    def handle(self, *args, **options):
        total = 0
        total += self._alertas_verificaciones()
        total += self._alertas_proyectos()
        total += self._alertas_qr()
        self.stdout.write(self.style.SUCCESS(f'✓ {total} notificaciones generadas'))

    # ------------------------------------------------------------------ #
    # Verificaciones por vencer o vencidas
    # ------------------------------------------------------------------ #
    def _alertas_verificaciones(self):
        from apps.verificacion.models import VerificacionEficacia, EstadoVerificacion
        from apps.notificaciones.utils import crear_notificacion, notificar_calidad
        from apps.notificaciones.models import TipoNotificacion

        hoy = timezone.now().date()
        en_7_dias = hoy + timezone.timedelta(days=7)
        count = 0

        pendientes = VerificacionEficacia.objects.filter(
            eliminado=False,
            estado__in=[EstadoVerificacion.PENDIENTE, EstadoVerificacion.EN_REVISION],
            fecha_objetivo__lte=en_7_dias,
        ).select_related('proyecto', 'proyecto__responsable', 'responsable')

        for ver in pendientes:
            try:
                url = reverse('verificacion:detalle', args=[ver.pk])
            except Exception:
                url = ''

            vencida = ver.fecha_objetivo < hoy
            dias = (ver.fecha_objetivo - hoy).days if not vencida else 0

            if vencida:
                titulo = f'Verificación VENCIDA: {ver.proyecto.folio}'
                mensaje = (f'La verificación del proyecto {ver.proyecto.folio} venció el '
                           f'{ver.fecha_objetivo.strftime("%d/%m/%Y")} y sigue pendiente.')
            else:
                titulo = f'Verificación por vencer en {dias} día(s): {ver.proyecto.folio}'
                mensaje = (f'La verificación del proyecto {ver.proyecto.folio} vence el '
                           f'{ver.fecha_objetivo.strftime("%d/%m/%Y")}.')

            notificar_calidad(TipoNotificacion.VERIFICACION_EFICACIA, titulo, mensaje, url)
            count += 1

            if ver.responsable_id:
                crear_notificacion(ver.responsable, TipoNotificacion.VERIFICACION_EFICACIA,
                                   titulo, mensaje, url)

        return count

    # ------------------------------------------------------------------ #
    # Proyectos con fecha fin pasada y aún en curso
    # ------------------------------------------------------------------ #
    def _alertas_proyectos(self):
        from apps.proyectos.models import Proyecto, EstadoProyecto
        from apps.notificaciones.utils import crear_notificacion, notificar_calidad
        from apps.notificaciones.models import TipoNotificacion
        from datetime import timedelta

        hoy = timezone.now().date()
        count = 0

        proyectos = Proyecto.objects.filter(
            eliminado=False,
            estado=EstadoProyecto.EN_CURSO,
        ).select_related('responsable')

        for p in proyectos:
            fecha_fin = p.fecha_inicio + timedelta(days=p.dias_ejecucion)
            if fecha_fin >= hoy:
                continue

            try:
                url = reverse('proyectos:detalle', args=[p.pk])
            except Exception:
                url = ''

            dias_atraso = (hoy - fecha_fin).days
            titulo = f'Proyecto atrasado {dias_atraso} día(s): {p.folio}'
            mensaje = (f'El proyecto "{p.nombre}" ({p.folio}) superó su fecha de fin estimada '
                       f'({fecha_fin.strftime("%d/%m/%Y")}) y continúa En Curso.')

            notificar_calidad(TipoNotificacion.PROYECTO_VENCIDO, titulo, mensaje, url)
            count += 1

            if p.responsable_id:
                crear_notificacion(p.responsable, TipoNotificacion.PROYECTO_VENCIDO,
                                   titulo, mensaje, url)

        return count

    # ------------------------------------------------------------------ #
    # QR sin respuesta superando días de resolución
    # ------------------------------------------------------------------ #
    def _alertas_qr(self):
        from apps.qr.models import QuejaReclamo, EstadoQR
        from apps.notificaciones.utils import crear_notificacion, notificar_calidad
        from apps.notificaciones.models import TipoNotificacion
        from datetime import timedelta

        hoy = timezone.now().date()
        count = 0

        abiertos = QuejaReclamo.objects.filter(
            eliminado=False,
            estado__in=[EstadoQR.BORRADOR, EstadoQR.EN_REVISION, EstadoQR.EN_SEGUIMIENTO],
            dias_resolucion__isnull=False,
        ).select_related('responsable')

        for qr in abiertos:
            fecha_limite = qr.fecha + timedelta(days=qr.dias_resolucion)
            if fecha_limite >= hoy:
                continue

            try:
                url = reverse('qr:detalle', args=[qr.pk])
            except Exception:
                url = ''

            dias_atraso = (hoy - fecha_limite).days
            titulo = f'Reclamo sin resolver ({dias_atraso} días): {qr.folio}'
            mensaje = (f'El reclamo {qr.folio} superó su plazo de resolución de '
                       f'{qr.dias_resolucion} días y continúa abierto.')

            notificar_calidad(TipoNotificacion.QR_SIN_RESPUESTA, titulo, mensaje, url)
            count += 1

            if qr.responsable_id:
                crear_notificacion(qr.responsable, TipoNotificacion.QR_SIN_RESPUESTA,
                                   titulo, mensaje, url)

        return count
