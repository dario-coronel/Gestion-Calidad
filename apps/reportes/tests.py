from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Rol, Usuario


class ReportesViewTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='reportes_user',
            password='Reporte1234!',
            rol=Rol.CALIDAD,
            is_active=True,
        )

    def test_lista_renderiza(self):
        self.client.login(username='reportes_user', password='Reporte1234!')
        response = self.client.get(reverse('reportes:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reportes')