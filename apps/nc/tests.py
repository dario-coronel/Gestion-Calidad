from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Usuario, Rol
from apps.nc.models import NoConformidad, EstadoNC, ClasificacionNC


class NCRoleWorkflowTests(TestCase):
    def setUp(self):
        self.operario = Usuario.objects.create_user(
            username='nc_operario',
            password='Operario1234!',
            rol=Rol.OPERARIO,
            is_active=True,
        )
        self.calidad = Usuario.objects.create_user(
            username='nc_calidad',
            password='Calidad1234!',
            rol=Rol.CALIDAD,
            is_active=True,
        )

    def test_operario_crea_nc_en_revision(self):
        self.client.login(username='nc_operario', password='Operario1234!')
        payload = {
            'fecha': '2026-04-24',
            'area': 'Laboratorio',
            'responsable': self.operario.pk,
            'id_muestra_lote': 'L-001',
            'parametro_afectado': 'Humedad',
            'descripcion': 'Descripcion de prueba',
            'prioridad': 'media',
            'clasificacion': ClasificacionNC.PROCESO,
        }
        response = self.client.post(reverse('nc:crear'), payload)
        self.assertEqual(response.status_code, 302)
        nc = NoConformidad.objects.latest('id')
        self.assertEqual(nc.estado, EstadoNC.EN_REVISION)

    def test_calidad_puede_reenviar_nc_a_borrador(self):
        nc = NoConformidad.objects.create(
            area='Laboratorio',
            responsable=self.operario,
            descripcion='NC a revisar',
            prioridad='media',
            clasificacion=ClasificacionNC.PROCESO,
            estado=EstadoNC.EN_REVISION,
            creado_por=self.operario,
            actualizado_por=self.operario,
        )
        self.client.login(username='nc_calidad', password='Calidad1234!')
        response = self.client.post(reverse('nc:detalle', args=[nc.pk]), {
            'accion': 'revision_calidad',
            'decision': 'reenviar',
        })
        self.assertEqual(response.status_code, 302)
        nc.refresh_from_db()
        self.assertEqual(nc.estado, EstadoNC.BORRADOR)
