from django import forms
from .models import NoConformidad, CincoPorques, AdjuntoNC, OrigenNC, EficaciaNC


class NoConformidadForm(forms.ModelForm):
    class Meta:
        model = NoConformidad
        fields = [
            'fecha', 'sector', 'responsable', 'id_muestra_lote',
            'parametro_afectado', 'descripcion', 'prioridad', 'clasificacion',
            # Origen
            'origen', 'qr_relacionada', 'om_relacionada',
            # Corrección
            'descripcion_correccion',
            # Contaminación cruzada
            'contaminacion_cruzada', 'tipo_contaminacion', 'obs_contaminacion',
            # Notificación cliente
            'notificar_cliente', 'email_cliente',
            # Evidencia
            'evidencia',
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'sector': forms.Select(attrs={'class': 'form-input'}),
            'id_muestra_lote': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: SU-A342'}),
            'parametro_afectado': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Humedad %'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 4,
                                                  'placeholder': 'Describí el problema detectado...'}),
            'prioridad': forms.Select(attrs={'class': 'form-input'}),
            'clasificacion': forms.Select(attrs={'class': 'form-input', 'id': 'id_clasificacion'}),
            'responsable': forms.Select(attrs={'class': 'form-input'}),
            'origen': forms.Select(attrs={'class': 'form-input', 'id': 'id_origen'}),
            'qr_relacionada': forms.Select(attrs={'class': 'form-input'}),
            'om_relacionada': forms.Select(attrs={'class': 'form-input'}),
            'descripcion_correccion': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 3,
                'placeholder': 'Describí la corrección inmediata aplicada...'
            }),
            'contaminacion_cruzada': forms.CheckboxInput(attrs={'class': 'form-checkbox', 'id': 'id_contaminacion_cruzada'}),
            'tipo_contaminacion': forms.RadioSelect(attrs={'class': 'radio-group'}),
            'obs_contaminacion': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 3,
                'placeholder': 'Observaciones sobre la contaminación cruzada...'
            }),
            'notificar_cliente': forms.CheckboxInput(attrs={'class': 'form-checkbox', 'id': 'id_notificar_cliente'}),
            'email_cliente': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'cliente@empresa.com'}),
            'evidencia': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 3,
                'placeholder': 'Describí la evidencia que demuestra la implementación...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.accounts.models import Usuario
        from apps.qr.models import QuejaReclamo
        from apps.om.models import OportunidadMejora
        from apps.core.models import Sector
        self.fields['sector'].queryset = Sector.objects.filter(activo=True).order_by('nombre')
        self.fields['sector'].empty_label = 'Seleccionar sector...'
        self.fields['sector'].required = False
        self.fields['responsable'].queryset = Usuario.objects.filter(is_active=True).order_by('first_name')
        self.fields['responsable'].empty_label = 'Seleccionar responsable...'
        self.fields['origen'].required = False
        self.fields['origen'].initial = OrigenNC.DIRECTO
        self.fields['qr_relacionada'].queryset = QuejaReclamo.objects.filter(eliminado=False).order_by('-fecha')
        self.fields['qr_relacionada'].empty_label = 'Seleccionar QyR...'
        self.fields['qr_relacionada'].required = False
        self.fields['om_relacionada'].queryset = OportunidadMejora.objects.filter(eliminado=False).order_by('-fecha')
        self.fields['om_relacionada'].empty_label = 'Seleccionar OM...'
        self.fields['om_relacionada'].required = False

    def clean(self):
        cleaned = super().clean()
        origen = cleaned.get('origen')
        qr = cleaned.get('qr_relacionada')
        om = cleaned.get('om_relacionada')
        contaminacion = cleaned.get('contaminacion_cruzada')
        tipo_contam = cleaned.get('tipo_contaminacion')
        notificar = cleaned.get('notificar_cliente')
        email = cleaned.get('email_cliente')

        if origen == OrigenNC.QR and not qr:
            self.add_error('qr_relacionada', 'Seleccioná la QyR asociada cuando el origen es Queja/Reclamo.')
        if origen == OrigenNC.OM and not om:
            self.add_error('om_relacionada', 'Seleccioná la OM asociada cuando el origen es Oportunidad de Mejora.')
        if contaminacion and not tipo_contam:
            self.add_error('tipo_contaminacion', 'Seleccioná el tipo de contaminación cruzada.')
        if notificar and not email:
            self.add_error('email_cliente', 'Ingresá el e-mail del cliente para enviar la notificación.')
        return cleaned


class MatrizRiesgoForm(forms.ModelForm):
    """Formulario para asignar probabilidad e impacto (solo Calidad/Manager)."""
    class Meta:
        model = NoConformidad
        fields = ['probabilidad', 'impacto']
        widgets = {
            'probabilidad': forms.Select(
                choices=[(i, f'{i}') for i in range(1, 6)],
                attrs={'class': 'form-input'}
            ),
            'impacto': forms.Select(
                choices=[(i, f'{i}') for i in range(1, 6)],
                attrs={'class': 'form-input'}
            ),
        }


class CincoPorquesForm(forms.ModelForm):
    class Meta:
        model = CincoPorques
        fields = ['etapa_1', 'etapa_2', 'etapa_3', 'etapa_4', 'etapa_5', 'causa_raiz', 'accion_correctiva']
        widgets = {
            'etapa_1': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'readonly': True}),
            'etapa_2': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': '¿Por qué? (Why 1)'}),
            'etapa_3': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': '¿Por qué? (Why 2)'}),
            'etapa_4': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': '¿Por qué? (Why 3)'}),
            'etapa_5': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': '¿Por qué? (Why 4)'}),
            'causa_raiz': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Causa raíz identificada (Why 5)'}),
            'accion_correctiva': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Acción correctiva propuesta...'}),
        }


class EficaciaForm(forms.ModelForm):
    """Formulario para que Calidad evalúe la eficacia de la acción correctiva."""
    class Meta:
        model = NoConformidad
        fields = ['eficacia', 'evidencia']
        widgets = {
            'eficacia': forms.RadioSelect(attrs={'class': 'radio-group'}),
            'evidencia': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 3,
                'placeholder': 'Describí la evidencia que demuestra la eficacia...'
            }),
        }


class AdjuntoNCForm(forms.ModelForm):
    class Meta:
        model = AdjuntoNC
        fields = ['archivo']
        widgets = {
            'archivo': forms.FileInput(attrs={'class': 'form-input', 'accept': '.jpg,.jpeg,.png,.pdf,.xlsx,.xls'}),
        }
