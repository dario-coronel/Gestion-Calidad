from django import forms
from django.conf import settings
from .models import QuejaReclamo, AdjuntoQR, TipoReclamo


class QuejaReclamoForm(forms.ModelForm):
    class Meta:
        model = QuejaReclamo
        fields = [
            'fecha', 'sector', 'responsable', 'id_cliente_pedido',
            'tipo_reclamo', 'id_muestra_lote', 'descripcion', 'prioridad', 'clasificacion',
            'nc_relacionada', 'om_asociada',
            'dias_resolucion', 'quien_recibe', 'detalle_visita_cliente',
            'acciones_a_tomar', 'acciones_a_tomar_correctivas', 'resultado', 'envio_mail', 'fecha_cierre',
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'sector': forms.Select(attrs={'class': 'form-input'}),
            'id_cliente_pedido': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: CLI-001 / PED-2026-042'}),
            'tipo_reclamo': forms.Select(attrs={'class': 'form-input'}),
            'id_muestra_lote': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Seleccionar o ingresar LOTE...',
                'list': 'lotes_sugeridos',
            }),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Describí el reclamo del cliente...'}),
            'prioridad': forms.Select(attrs={'class': 'form-input'}),
            'clasificacion': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Clasificación adicional (opcional)'}),
            'nc_relacionada': forms.Select(attrs={'class': 'form-input'}),
            'om_asociada': forms.Select(attrs={'class': 'form-input'}),
            'responsable': forms.Select(attrs={'class': 'form-input'}),
            'dias_resolucion': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 5', 'min': 1}),
            'quien_recibe': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre de quien recibe la queja'}),
            'detalle_visita_cliente': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Detallá la visita o contacto con el cliente...'}),
            'acciones_a_tomar': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Describí las acciones acordadas...'}),
            'acciones_a_tomar_correctivas': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Describí las acciones correctivas...'}),
            'resultado': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Resultado final de la gestión...'}),
            'envio_mail': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-teal-600 border-gray-300 rounded'}),
            'fecha_cierre': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.accounts.models import Usuario
        from apps.core.models import Sector
        from apps.nc.models import NoConformidad
        from apps.om.models import OportunidadMejora

        self.fields['sector'].queryset = Sector.objects.filter(activo=True).order_by('nombre')
        self.fields['sector'].empty_label = 'Seleccionar sector...'
        self.fields['sector'].required = False

        self.fields['responsable'].queryset = Usuario.objects.filter(is_active=True).order_by('first_name')
        self.fields['responsable'].empty_label = 'Seleccionar responsable...'

        self.fields['nc_relacionada'].queryset = NoConformidad.objects.filter(eliminado=False).order_by('-fecha')
        self.fields['nc_relacionada'].empty_label = 'Seleccionar NC...'
        self.fields['nc_relacionada'].required = False

        self.fields['om_asociada'].queryset = OportunidadMejora.objects.filter(eliminado=False).order_by('-fecha')
        self.fields['om_asociada'].empty_label = 'Seleccionar OM...'
        self.fields['om_asociada'].required = False

        lotes = (
            NoConformidad.objects
            .filter(eliminado=False)
            .exclude(id_muestra_lote='')
            .order_by('id_muestra_lote')
            .values_list('id_muestra_lote', flat=True)
            .distinct()
        )
        lote_choices = [(lote, lote) for lote in lotes]
        lote_actual = getattr(self.instance, 'id_muestra_lote', '') if self.instance else ''
        if lote_actual and lote_actual not in {value for value, _ in lote_choices}:
            lote_choices.append((lote_actual, lote_actual))
        self.lotes_sugeridos = [value for value, _ in lote_choices]
        self.fields['id_muestra_lote'].required = False

        self.fields['dias_resolucion'].label = 'Tiempo de respuesta (días)'
        self.fields['fecha_cierre'].required = False

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo_reclamo')
        nc = cleaned.get('nc_relacionada')
        lote = (cleaned.get('id_muestra_lote') or '').strip()
        required_types = {str(v).strip() for v in getattr(settings, 'QR_REQUIRED_NC_TYPES', []) if str(v).strip()}

        if tipo in required_types and not nc:
            self.add_error('nc_relacionada', 'Este tipo de reclamo requiere una NC asociada.')

        if tipo == TipoReclamo.CALIDAD_PRODUCTO and not lote:
            self.add_error('id_muestra_lote', 'Para Calidad del Producto en Destino debés indicar el LOTE.')

        if tipo != TipoReclamo.CALIDAD_PRODUCTO:
            cleaned['id_muestra_lote'] = ''
        else:
            cleaned['id_muestra_lote'] = lote

        return cleaned


class AdjuntoQRForm(forms.ModelForm):
    class Meta:
        model = AdjuntoQR
        fields = ['archivo']
        widgets = {
            'archivo': forms.FileInput(attrs={'class': 'form-input', 'accept': '.jpg,.jpeg,.png,.pdf,.xlsx,.xls'}),
        }
