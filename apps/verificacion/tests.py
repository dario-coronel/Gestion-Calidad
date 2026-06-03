from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.core.management import call_command

from apps.accounts.models import Rol, Usuario
from apps.core.models import Sector
from apps.proyectos.models import OrigenProyecto, Proyecto
from apps.verificacion.forms import VerificacionForm
from apps.verificacion.models import EstadoVerificacion, VerificacionEficacia


class VerificacionWorkflowTests(TestCase):
    def setUp(self):
        call_command('seed_grupos', solo_grupos=True, verbosity=0)
        self.calidad = Usuario.objects.create_user(
            username='verif_calidad',
            password='Calidad1234!',
            rol=Rol.CALIDAD,
            is_active=True,
        )
        self.sector, _ = Sector.objects.get_or_create(nombre='Laboratorio')
        self.proyecto = Proyecto.objects.create(
            nombre='Proyecto verificacion',
            sector=self.sector,
            prioridad='media',
            responsable=self.calidad,
            fecha_inicio=date(2026, 4, 1),
            dias_ejecucion=10,
            proveedor='Interno',
            origen=OrigenProyecto.INDEPENDIENTE,
            creado_por=self.calidad,
            actualizado_por=self.calidad,
        )
        self.ver = VerificacionEficacia.objects.create(
            proyecto=self.proyecto,
            fecha_cierre_proyecto=date(2026, 4, 11),
            fecha_objetivo=date(2026, 7, 10),
            responsable=self.calidad,
        )

    def test_no_eficaz_genera_nc_automatica(self):
        self.client.login(username='verif_calidad', password='Calidad1234!')
        response = self.client.post(reverse('verificacion:detalle', args=[self.ver.pk]), {
            'responsable': self.calidad.pk,
            'fecha_realizada': '2026-07-11',
            'estado': EstadoVerificacion.NO_EFICAZ,
            'resultado_descripcion': 'No se sostuvo la mejora.',
        })
        self.assertEqual(response.status_code, 302)
        self.ver.refresh_from_db()
        self.assertIsNotNone(self.ver.nc_generada)
        self.assertEqual(self.ver.nc_generada.sector, self.sector)

    def test_form_edicion_muestra_fecha_realizada_guardada(self):
        self.ver.fecha_realizada = date(2026, 7, 11)
        self.ver.save(update_fields=['fecha_realizada', 'actualizado_en'])

        form = VerificacionForm(instance=self.ver)
        self.assertIn('value="2026-07-11"', str(form['fecha_realizada']))
