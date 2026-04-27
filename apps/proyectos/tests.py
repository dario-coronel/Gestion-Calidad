from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Rol, Usuario
from apps.core.models import Sector
from apps.nc.models import ClasificacionNC, EstadoNC, NoConformidad
from apps.om.models import ClasificacionOM, OportunidadMejora
from apps.proyectos.models import EstadoProyecto, OrigenProyecto, Proyecto


class ProyectoWorkflowTests(TestCase):
    def setUp(self):
        self.calidad = Usuario.objects.create_user(
            username='proy_calidad',
            password='Calidad1234!',
            rol=Rol.CALIDAD,
            is_active=True,
        )
        self.sector, _ = Sector.objects.get_or_create(nombre='Logistica')
        self.om = OportunidadMejora.objects.create(
            fecha=date(2026, 4, 24),
            sector=self.sector,
            responsable=self.calidad,
            clasificacion=ClasificacionOM.CALIDAD,
            descripcion='OM de origen',
            beneficio_potencial='media',
            creado_por=self.calidad,
            actualizado_por=self.calidad,
        )

    def test_calidad_crea_proyecto_desde_om(self):
        self.client.login(username='proy_calidad', password='Calidad1234!')
        response = self.client.post(reverse('proyectos:crear'), {
            'nombre': 'Implementacion de mejora OM',
            'sector': self.sector.pk,
            'prioridad': 'media',
            'responsable': self.calidad.pk,
            'fecha_inicio': '2026-04-24',
            'dias_ejecucion': 15,
            'proveedor': 'Interno',
            'origen': OrigenProyecto.OM,
            'om': self.om.pk,
        })
        self.assertEqual(response.status_code, 302)
        proyecto = Proyecto.objects.latest('id')
        self.assertEqual(proyecto.om, self.om)
        self.assertEqual(proyecto.origen, OrigenProyecto.OM)
        self.assertEqual(proyecto.sector, self.sector)

    def test_nc_aprobada_crea_proyecto_con_sector(self):
        nc = NoConformidad.objects.create(
            fecha=date(2026, 4, 24),
            sector=self.sector,
            responsable=self.calidad,
            descripcion='NC aprobada',
            prioridad='media',
            clasificacion=ClasificacionNC.PROCESO,
            estado=EstadoNC.APROBADA,
            creado_por=self.calidad,
            actualizado_por=self.calidad,
        )
        proyecto = nc.proyecto
        self.assertEqual(proyecto.origen, OrigenProyecto.NC)
        self.assertEqual(proyecto.sector, self.sector)

    def test_finalizar_proyecto_crea_verificacion(self):
        proyecto = Proyecto.objects.create(
            nombre='Proyecto a finalizar',
            sector=self.sector,
            prioridad='media',
            responsable=self.calidad,
            fecha_inicio=date(2026, 4, 24),
            dias_ejecucion=10,
            proveedor='Interno',
            origen=OrigenProyecto.INDEPENDIENTE,
            creado_por=self.calidad,
            actualizado_por=self.calidad,
        )
        proyecto.estado = EstadoProyecto.FINALIZADO
        proyecto.save()

        proyecto.refresh_from_db()
        self.assertTrue(hasattr(proyecto, 'verificacion_eficacia'))
        self.assertEqual(proyecto.verificacion_eficacia.responsable, self.calidad)