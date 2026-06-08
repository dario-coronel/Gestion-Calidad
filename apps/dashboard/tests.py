from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Rol, Usuario
from apps.core.models import Clasificacion, Responsable, Sector
from apps.om.models import EstadoOM, OportunidadMejora
from apps.qr.models import EstadoQR, QuejaReclamo, TipoReclamo


class DashboardQrKpiTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username='dashboard_admin',
            password='Admin1234!',
            rol=Rol.ADMIN,
            is_superuser=True,
            is_staff=True,
            is_active=True,
        )
        self.sector, _ = Sector.objects.get_or_create(nombre='Calidad')
        self.clasificacion_calidad, _ = Clasificacion.objects.get_or_create(nombre='Calidad')
        self.responsable_user, _ = Responsable.objects.get_or_create(
            usuario=self.user,
            defaults={'nombre': 'Dashboard Admin', 'activo': True},
        )

    def _crear_qr(self, *, fecha, estado=EstadoQR.BORRADOR, dias_resolucion=10, fecha_cierre=None):
        return QuejaReclamo.objects.create(
            fecha=fecha,
            sector=self.sector,
            responsable=self.responsable_user,
            id_cliente_pedido='CLI-001/PED-001',
            tipo_reclamo=TipoReclamo.OTRO,
            descripcion='Reclamo de prueba',
            prioridad='media',
            clasificacion='General',
            estado=estado,
            dias_resolucion=dias_resolucion,
            fecha_cierre=fecha_cierre,
            creado_por=self.user,
            actualizado_por=self.user,
        )

    def _crear_om(self, *, fecha, estado=EstadoOM.BORRADOR):
        return OportunidadMejora.objects.create(
            fecha=fecha,
            sector=self.sector,
            responsable=self.responsable_user,
            descripcion='OM de prueba',
            clasificacion=self.clasificacion_calidad.nombre,
            estado=estado,
            creado_por=self.user,
            actualizado_por=self.user,
        )

    def test_dashboard_muestra_kpis_y_tendencia_qr(self):
        hoy = timezone.localdate()
        self._crear_qr(fecha=hoy - timedelta(days=5), estado=EstadoQR.BORRADOR, dias_resolucion=3)
        self._crear_qr(fecha=hoy - timedelta(days=40), estado=EstadoQR.CERRADO, dias_resolucion=15)
        self._crear_om(fecha=hoy - timedelta(days=3), estado=EstadoOM.BORRADOR)
        self._crear_om(fecha=hoy - timedelta(days=1), estado=EstadoOM.CERRADA)
        self._crear_om(fecha=hoy - timedelta(days=60), estado=EstadoOM.CERRADA)

        self.client.login(username='dashboard_admin', password='Admin1234!')
        response = self.client.get(reverse('dashboard:index'), {'period': '30d'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['qr_period'], '30d')
        self.assertEqual(response.context['kpi_total_qr'], 1)
        self.assertEqual(response.context['kpi_qr_abiertas'], 1)
        self.assertEqual(response.context['kpi_qr_vencidas'], 1)
        self.assertIsNone(response.context['kpi_qr_dias_promedio'])
        self.assertEqual(response.context['kpi_total_om'], 2)
        self.assertEqual(response.context['kpi_om_abiertas'], 1)
        self.assertEqual(response.context['kpi_om_cerradas'], 1)
        self.assertIn('Últimos 30 días', response.context['qr_period_label'])
        self.assertTrue(response.context['qr_trend_labels_json'])
        self.assertTrue(response.context['qr_trend_values_json'])
        self.assertTrue(response.context['om_estado_labels_json'])
        self.assertTrue(response.context['om_estado_data_json'])

    def test_dashboard_calcula_qyr_dias_promedio_con_cierre_real_en_periodo(self):
        hoy = timezone.localdate()
        self._crear_qr(
            fecha=hoy - timedelta(days=12),
            estado=EstadoQR.CERRADO,
            dias_resolucion=None,
            fecha_cierre=hoy - timedelta(days=6),
        )
        self._crear_qr(
            fecha=hoy - timedelta(days=8),
            estado=EstadoQR.CERRADO,
            dias_resolucion=None,
            fecha_cierre=hoy - timedelta(days=4),
        )
        # Fuera del rango de 30d, no debe impactar el promedio para ese período.
        self._crear_qr(
            fecha=hoy - timedelta(days=60),
            estado=EstadoQR.CERRADO,
            dias_resolucion=None,
            fecha_cierre=hoy - timedelta(days=55),
        )

        self.client.login(username='dashboard_admin', password='Admin1234!')
        response = self.client.get(reverse('dashboard:index'), {'period': '30d'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['kpi_qr_dias_promedio'], 5.0)