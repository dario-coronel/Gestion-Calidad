from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.core.management import call_command
from django.test.utils import override_settings

from apps.accounts.models import Usuario, Rol
from apps.core.models import Sector
from apps.qr.models import QuejaReclamo, EstadoQR, TipoReclamo
from apps.om.models import OportunidadMejora, ClasificacionOM
from apps.nc.models import NoConformidad, ClasificacionNC
from apps.qr.forms import QuejaReclamoForm


class QRRoleWorkflowTests(TestCase):
    def setUp(self):
        call_command('seed_grupos', solo_grupos=True, verbosity=0)
        self.operario = Usuario.objects.create_user(
            username='qr_operario',
            password='Operario1234!',
            rol=Rol.OPERARIO,
            is_active=True,
        )
        self.calidad = Usuario.objects.create_user(
            username='qr_calidad',
            password='Calidad1234!',
            rol=Rol.CALIDAD,
            is_active=True,
        )
        self.sector, _ = Sector.objects.get_or_create(nombre='Comercial')

    def test_operario_crea_qr_en_revision(self):
        self.client.login(username='qr_operario', password='Operario1234!')
        payload = {
            'fecha': '2026-04-24',
            'sector': self.sector.pk,
            'responsable': self.operario.pk,
            'id_cliente_pedido': 'CLI-001/PED-001',
            'tipo_reclamo': TipoReclamo.OTRO,
            'descripcion': 'Reclamo de prueba',
            'prioridad': 'media',
            'clasificacion': 'General',
        }
        response = self.client.post(reverse('qr:crear'), payload)
        self.assertEqual(response.status_code, 302)
        qr = QuejaReclamo.objects.latest('id')
        self.assertEqual(qr.estado, EstadoQR.EN_REVISION)

    def test_calidad_acepta_qr_y_pasa_a_seguimiento(self):
        qr = QuejaReclamo.objects.create(
            sector=self.sector,
            responsable=self.operario,
            id_cliente_pedido='CLI-001/PED-001',
            tipo_reclamo=TipoReclamo.OTRO,
            descripcion='Reclamo a revisar',
            prioridad='media',
            clasificacion='General',
            estado=EstadoQR.EN_REVISION,
            creado_por=self.operario,
            actualizado_por=self.operario,
        )
        self.client.login(username='qr_calidad', password='Calidad1234!')
        response = self.client.post(reverse('qr:detalle', args=[qr.pk]), {
            'accion': 'revision_calidad',
            'decision': 'aprobar',
        })
        self.assertEqual(response.status_code, 302)
        qr.refresh_from_db()
        self.assertEqual(qr.estado, EstadoQR.EN_SEGUIMIENTO)
        self.assertIsNotNone(qr.om_asociada)
        self.assertTrue(OportunidadMejora.objects.filter(pk=qr.om_asociada_id).exists())


class QRBackfillAndValidationTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username='qr_backfill_user',
            password='Backfill1234!',
            rol=Rol.CALIDAD,
            is_active=True,
        )
        self.sector, _ = Sector.objects.get_or_create(nombre='Laboratorio')

    def test_backfill_qr_links_desde_nc(self):
        qr = QuejaReclamo.objects.create(
            sector=self.sector,
            responsable=self.user,
            id_cliente_pedido='CLI-888/PED-999',
            tipo_reclamo=TipoReclamo.DOCUMENTACION,
            descripcion='Reclamo legacy',
            prioridad='media',
            clasificacion='Legacy',
            estado=EstadoQR.EN_REVISION,
            creado_por=self.user,
            actualizado_por=self.user,
        )
        om = OportunidadMejora.objects.create(
            sector=self.sector,
            responsable=self.user,
            descripcion='OM histórica',
            beneficio_potencial='media',
            clasificacion=ClasificacionOM.CALIDAD,
            creado_por=self.user,
            actualizado_por=self.user,
        )
        NoConformidad.objects.create(
            sector=self.sector,
            responsable=self.user,
            descripcion='NC histórica ligada a QyR',
            prioridad='media',
            clasificacion=ClasificacionNC.PROCESO,
            qr_relacionada=qr,
            om_relacionada=om,
            creado_por=self.user,
            actualizado_por=self.user,
        )

        call_command('backfill_qr_links', verbosity=0)

        qr.refresh_from_db()
        self.assertIsNotNone(qr.nc_relacionada)
        self.assertEqual(qr.om_asociada, om)

    @override_settings(QR_REQUIRED_NC_TYPES=[TipoReclamo.DOCUMENTACION])
    def test_validacion_opcional_exige_nc_segun_tipo(self):
        form = QuejaReclamoForm(data={
            'fecha': '2026-05-06',
            'sector': self.sector.pk,
            'responsable': self.user.pk,
            'id_cliente_pedido': 'CLI-001/PED-002',
            'tipo_reclamo': TipoReclamo.DOCUMENTACION,
            'descripcion': 'Falta documentación adjunta',
            'prioridad': 'media',
            'clasificacion': 'General',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('nc_relacionada', form.errors)

    def test_permite_seleccionar_id_muestra_lote_para_calidad_producto(self):
        nc = NoConformidad.objects.create(
            fecha=date(2026, 5, 6),
            sector=self.sector,
            responsable=self.user,
            id_muestra_lote='LOTE-ABC-123',
            descripcion='NC con lote para trazabilidad',
            prioridad='media',
            clasificacion=ClasificacionNC.PROCESO,
            creado_por=self.user,
            actualizado_por=self.user,
        )

        form = QuejaReclamoForm(data={
            'fecha': '2026-05-07',
            'sector': self.sector.pk,
            'responsable': self.user.pk,
            'id_cliente_pedido': 'CLI-009/PED-010',
            'tipo_reclamo': TipoReclamo.CALIDAD_PRODUCTO,
            'id_muestra_lote': nc.id_muestra_lote,
            'descripcion': 'Reclamo por desvío de calidad detectado en destino',
            'prioridad': 'alta',
            'clasificacion': 'Calidad',
        })

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['id_muestra_lote'], 'LOTE-ABC-123')

    def test_exige_lote_cuando_tipo_es_calidad_producto(self):
        form = QuejaReclamoForm(data={
            'fecha': '2026-05-07',
            'sector': self.sector.pk,
            'responsable': self.user.pk,
            'id_cliente_pedido': 'CLI-010/PED-011',
            'tipo_reclamo': TipoReclamo.CALIDAD_PRODUCTO,
            'id_muestra_lote': '',
            'descripcion': 'Reclamo por calidad sin lote informado',
            'prioridad': 'alta',
            'clasificacion': 'Calidad',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('id_muestra_lote', form.errors)
