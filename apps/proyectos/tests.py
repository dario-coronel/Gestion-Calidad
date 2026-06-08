from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.core.management import call_command

from apps.accounts.models import Rol, Usuario
from apps.core.models import Clasificacion, Responsable, Sector
from apps.nc.models import ClasificacionNC, EstadoNC, NoConformidad
from apps.om.models import OportunidadMejora
from apps.proyectos.forms import ProyectoForm
from apps.proyectos.models import EstadoProyecto, OrigenProyecto, Proyecto


class ProyectoWorkflowTests(TestCase):
    def setUp(self):
        call_command('seed_grupos', solo_grupos=True, verbosity=0)
        self.calidad = Usuario.objects.create_user(
            username='proy_calidad',
            password='Calidad1234!',
            rol=Rol.CALIDAD,
            is_active=True,
        )
        self.sector, _ = Sector.objects.get_or_create(nombre='Logistica')
        self.clasificacion_calidad, _ = Clasificacion.objects.get_or_create(nombre='Calidad')
        self.responsable_calidad, _ = Responsable.objects.get_or_create(
            usuario=self.calidad,
            defaults={'nombre': 'Calidad Proyectos Test', 'activo': True},
        )
        self.om = OportunidadMejora.objects.create(
            fecha=date(2026, 4, 24),
            sector=self.sector,
            responsable=self.responsable_calidad,
            clasificacion=self.clasificacion_calidad.nombre,
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
            'responsable': self.responsable_calidad.pk,
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
            responsable=self.responsable_calidad,
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
            responsable=self.responsable_calidad,
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
        self.assertEqual(proyecto.verificacion_eficacia.responsable, self.responsable_calidad)

    def test_form_edicion_muestra_fecha_inicio_guardada(self):
        proyecto = Proyecto.objects.create(
            nombre='Proyecto con fecha fija',
            sector=self.sector,
            prioridad='media',
            responsable=self.responsable_calidad,
            fecha_inicio=date(2026, 5, 3),
            dias_ejecucion=10,
            proveedor='Interno',
            origen=OrigenProyecto.INDEPENDIENTE,
            creado_por=self.calidad,
            actualizado_por=self.calidad,
        )

        form = ProyectoForm(instance=proyecto)
        self.assertIn('value="2026-05-03"', str(form['fecha_inicio']))