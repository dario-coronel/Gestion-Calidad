from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.core.management import call_command

from apps.accounts.models import Usuario, Rol
from apps.core.models import Responsable, Sector
from apps.nc.forms import NoConformidadForm, EficaciaForm
from apps.nc.models import NoConformidad, EstadoNC, ClasificacionNC, NormaNC, PuntoNormaNC, EficaciaNC
from apps.om.models import OportunidadMejora, EstadoOM


class NCRoleWorkflowTests(TestCase):
    def setUp(self):
        call_command('seed_grupos', solo_grupos=True, verbosity=0)
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
        self.sector, _ = Sector.objects.get_or_create(nombre='Laboratorio')
        self.responsable_operario, _ = Responsable.objects.get_or_create(
            usuario=self.operario,
            defaults={'nombre': 'Operario NC Test', 'activo': True},
        )
        self.norma = NormaNC.objects.create(
            nombre='ISO 9001:2015',
            creado_por=self.calidad,
            actualizado_por=self.calidad,
        )
        self.punto_norma = PuntoNormaNC.objects.create(
            norma=self.norma,
            codigo='8.7',
            descripcion='Control de las salidas no conformes',
            creado_por=self.calidad,
            actualizado_por=self.calidad,
        )

    def test_operario_crea_nc_en_revision(self):
        self.client.login(username='nc_operario', password='Operario1234!')
        payload = {
            'fecha': '2026-04-24',
            'sector': self.sector.pk,
            'responsable': self.responsable_operario.pk,
            'id_muestra_lote': 'L-001',
            'parametro_afectado': 'Humedad',
            'norma': self.norma.pk,
            'punto_norma': self.punto_norma.pk,
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
            sector=self.sector,
            responsable=self.responsable_operario,
            norma=self.norma,
            punto_norma=self.punto_norma,
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

    def test_creacion_nc_rechaza_punto_de_otra_norma(self):
        otra_norma = NormaNC.objects.create(
            nombre='BPM',
            creado_por=self.calidad,
            actualizado_por=self.calidad,
        )
        punto_otra_norma = PuntoNormaNC.objects.create(
            norma=otra_norma,
            codigo='4.1',
            descripcion='Condiciones edilicias',
            creado_por=self.calidad,
            actualizado_por=self.calidad,
        )

        self.client.login(username='nc_operario', password='Operario1234!')
        response = self.client.post(reverse('nc:crear'), {
            'fecha': '2026-04-24',
            'sector': self.sector.pk,
            'responsable': self.responsable_operario.pk,
            'norma': self.norma.pk,
            'punto_norma': punto_otra_norma.pk,
            'descripcion': 'Descripcion de prueba',
            'prioridad': 'media',
            'clasificacion': ClasificacionNC.PROCESO,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'El punto seleccionado no corresponde a la norma elegida.')

    def test_crear_punto_reactiva_duplicado_eliminado(self):
        self.punto_norma.eliminado = True
        self.punto_norma.actualizado_por = self.calidad
        self.punto_norma.save(update_fields=['eliminado', 'actualizado_por', 'actualizado_en'])

        self.client.login(username='nc_calidad', password='Calidad1234!')
        response = self.client.post(reverse('nc:punto_crear', args=[self.norma.pk]), {
            'codigo': '8.7',
            'descripcion': 'Control de las salidas no conformes',
            'activo': 'on',
        })

        self.assertEqual(response.status_code, 302)
        self.punto_norma.refresh_from_db()
        self.assertFalse(self.punto_norma.eliminado)
        self.assertTrue(self.punto_norma.activo)
        self.assertEqual(
            PuntoNormaNC.objects.filter(
                norma=self.norma,
                codigo='8.7',
                descripcion='Control de las salidas no conformes',
            ).count(),
            1,
        )

    def test_form_edicion_muestra_fechas_guardadas(self):
        nc = NoConformidad.objects.create(
            fecha=date(2026, 5, 4),
            fecha_implementacion_accion=date(2026, 5, 10),
            sector=self.sector,
            responsable=self.responsable_operario,
            norma=self.norma,
            punto_norma=self.punto_norma,
            descripcion='NC para validar fecha en edición',
            prioridad='media',
            clasificacion=ClasificacionNC.PROCESO,
            creado_por=self.operario,
            actualizado_por=self.operario,
        )

        form = NoConformidadForm(instance=nc)
        self.assertIn('value="2026-05-04"', str(form['fecha']))
        self.assertIn('value="2026-05-10"', str(form['fecha_implementacion_accion']))

    def test_operario_puede_asociar_om_existente_desde_formulario_nc(self):
        om = OportunidadMejora.objects.create(
            fecha=date(2026, 4, 1),
            sector=self.sector,
            responsable=self.responsable_operario,
            descripcion='OM existente para asociar a NC',
            clasificacion='Calidad',
            estado=EstadoOM.IMPLEMENTADA,
            creado_por=self.calidad,
            actualizado_por=self.calidad,
        )

        self.client.login(username='nc_operario', password='Operario1234!')
        response = self.client.post(reverse('nc:crear'), {
            'fecha': '2026-04-24',
            'sector': self.sector.pk,
            'responsable': self.responsable_operario.pk,
            'id_muestra_lote': 'L-002',
            'parametro_afectado': 'Proteina',
            'norma': self.norma.pk,
            'punto_norma': self.punto_norma.pk,
            'descripcion': 'NC con OM asociada',
            'prioridad': 'media',
            'clasificacion': ClasificacionNC.PROCESO,
            'origen': 'directo',
            'om_relacionada': om.pk,
        })

        self.assertEqual(response.status_code, 302)
        nc = NoConformidad.objects.latest('id')
        self.assertEqual(nc.om_relacionada_id, om.pk)

    def test_operario_puede_crear_nc_con_origen_om_sin_om_asociada(self):
        self.client.login(username='nc_operario', password='Operario1234!')
        response = self.client.post(reverse('nc:crear'), {
            'fecha': '2026-04-25',
            'sector': self.sector.pk,
            'responsable': self.responsable_operario.pk,
            'id_muestra_lote': 'L-003',
            'parametro_afectado': 'Cenizas',
            'norma': self.norma.pk,
            'punto_norma': self.punto_norma.pk,
            'descripcion': 'NC origen OM, sin OM al momento de crear',
            'prioridad': 'media',
            'clasificacion': ClasificacionNC.PROCESO,
            'origen': 'om',
            'om_relacionada': '',
        })

        self.assertEqual(response.status_code, 302)
        nc = NoConformidad.objects.latest('id')
        self.assertEqual(nc.origen, 'om')
        self.assertIsNone(nc.om_relacionada)

    def test_eficacia_nc_exige_explicacion_si_es_eficaz(self):
        nc = NoConformidad.objects.create(
            sector=self.sector,
            responsable=self.responsable_operario,
            norma=self.norma,
            punto_norma=self.punto_norma,
            descripcion='NC para validación de eficacia',
            prioridad='media',
            clasificacion=ClasificacionNC.PROCESO,
            estado=EstadoNC.EN_IMPLEMENTACION,
            creado_por=self.operario,
            actualizado_por=self.operario,
        )

        form_invalido = EficaciaForm(data={
            'eficacia': EficaciaNC.EFICAZ,
            'explicacion_eficacia': '',
            'evidencia': 'Se verificó implementación.',
        }, instance=nc)
        self.assertFalse(form_invalido.is_valid())
        self.assertIn('explicacion_eficacia', form_invalido.errors)

        form_valido = EficaciaForm(data={
            'eficacia': EficaciaNC.EFICAZ,
            'explicacion_eficacia': 'Se repitió el proceso sin desvíos durante 3 lotes consecutivos.',
            'evidencia': 'Registros de control y acta de cierre.',
        }, instance=nc)
        self.assertTrue(form_valido.is_valid())
