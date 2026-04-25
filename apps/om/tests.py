from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Usuario, Rol
from apps.om.models import OportunidadMejora, EstadoOM, ClasificacionOM


class OMRoleWorkflowTests(TestCase):
    def setUp(self):
        self.operario = Usuario.objects.create_user(
            username='om_operario',
            password='Operario1234!',
            rol=Rol.OPERARIO,
            is_active=True,
        )
        self.calidad = Usuario.objects.create_user(
            username='om_calidad',
            password='Calidad1234!',
            rol=Rol.CALIDAD,
            is_active=True,
        )

    def test_operario_crea_om_en_revision(self):
        self.client.login(username='om_operario', password='Operario1234!')
        payload = {
            'fecha': '2026-04-24',
            'sector': 'Produccion',
            'responsable': self.operario.pk,
            'clasificacion': ClasificacionOM.CALIDAD,
            'descripcion': 'OM de prueba',
            'beneficio_potencial': 'media',
        }
        response = self.client.post(reverse('om:crear'), payload)
        self.assertEqual(response.status_code, 302)
        om = OportunidadMejora.objects.latest('id')
        self.assertEqual(om.estado, EstadoOM.EN_REVISION)

    def test_calidad_rechaza_om(self):
        om = OportunidadMejora.objects.create(
            sector='Produccion',
            responsable=self.operario,
            clasificacion=ClasificacionOM.CALIDAD,
            descripcion='OM para rechazo',
            beneficio_potencial='media',
            estado=EstadoOM.EN_REVISION,
            creado_por=self.operario,
            actualizado_por=self.operario,
        )
        self.client.login(username='om_calidad', password='Calidad1234!')
        response = self.client.post(reverse('om:detalle', args=[om.pk]), {
            'accion': 'revision_calidad',
            'decision': 'rechazar',
        })
        self.assertEqual(response.status_code, 302)
        om.refresh_from_db()
        self.assertEqual(om.estado, EstadoOM.RECHAZADA)
