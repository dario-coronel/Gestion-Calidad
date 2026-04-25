from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Usuario, Rol


class UsuariosManagementTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(
            username='admin_test',
            password='Admin1234!',
            rol=Rol.ADMIN,
            is_superuser=True,
            is_staff=True,
        )
        self.operario = Usuario.objects.create_user(
            username='operario_test',
            password='Operario1234!',
            rol=Rol.OPERARIO,
        )

    def test_operario_no_puede_ver_gestion_usuarios(self):
        self.client.login(username='operario_test', password='Operario1234!')
        response = self.client.get(reverse('accounts:usuarios_lista'))
        self.assertEqual(response.status_code, 302)

    def test_admin_puede_crear_usuario(self):
        self.client.login(username='admin_test', password='Admin1234!')
        payload = {
            'username': 'nuevo_usuario',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'email': 'nuevo@example.com',
            'rol': Rol.CALIDAD,
            'area': 'Calidad',
            'telefono': '123',
            'is_active': True,
            'password1': 'ClaveSegura123!',
            'password2': 'ClaveSegura123!',
        }
        response = self.client.post(reverse('accounts:usuarios_crear'), payload)
        self.assertEqual(response.status_code, 302)
        creado = Usuario.objects.get(username='nuevo_usuario')
        self.assertEqual(creado.rol, Rol.CALIDAD)
