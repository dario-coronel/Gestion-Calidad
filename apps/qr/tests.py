from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Usuario, Rol
from apps.qr.models import QuejaReclamo, EstadoQR, TipoReclamo


class QRRoleWorkflowTests(TestCase):
    def setUp(self):
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

    def test_operario_crea_qr_en_revision(self):
        self.client.login(username='qr_operario', password='Operario1234!')
        payload = {
            'fecha': '2026-04-24',
            'area_origen': 'Ventas',
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
            area_origen='Ventas',
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
