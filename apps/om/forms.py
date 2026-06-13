from django import forms
from .models import OportunidadMejora, AdjuntoOM, EficaciaOM


class OportunidadMejoraForm(forms.ModelForm):
    clasificacion = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-input'}),
    )

    class Meta:
        model = OportunidadMejora
        fields = [
            'fecha', 'sector', 'responsable', 'clasificacion',
            'descripcion', 'problema_a_mejorar', 'beneficio_potencial',
            'rango_evaluacion',
        ]
        widgets = {
            'fecha': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-input'}),
            'sector': forms.Select(attrs={'class': 'form-input'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Describí la oportunidad o sugerencia de mejora...'}),
            'problema_a_mejorar': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Describí el problema o área a mejorar...'}),
            'beneficio_potencial': forms.Select(attrs={'class': 'form-input'}),
            'responsable': forms.Select(attrs={'class': 'form-input'}),
            'rango_evaluacion': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.core.models import Sector, Clasificacion, Responsable
        self.fields['sector'].queryset = Sector.objects.filter(activo=True).order_by('nombre')
        self.fields['sector'].empty_label = 'Seleccionar sector...'
        self.fields['sector'].required = False
        clasificaciones = [c.nombre for c in Clasificacion.objects.filter(activo=True).order_by('nombre')]
        clasificacion_actual = (getattr(self.instance, 'clasificacion', '') or '').strip() if self.instance else ''
        if clasificacion_actual and clasificacion_actual not in clasificaciones:
            clasificaciones.append(clasificacion_actual)
        self.fields['clasificacion'].choices = [('', 'Seleccionar clasificación...')] + [
            (nombre, nombre) for nombre in clasificaciones
        ]
        self.fields['responsable'].queryset = Responsable.objects.filter(activo=True).order_by('nombre')
        self.fields['responsable'].empty_label = 'Seleccionar responsable...'
        self.fields['rango_evaluacion'].empty_label = 'Sin definir'
        self.fields['fecha'].localize = False
        self.fields['fecha'].widget.is_localized = False
        self.fields['fecha'].widget.format = '%Y-%m-%d'


class EficaciaOMForm(forms.ModelForm):
    class Meta:
        model = OportunidadMejora
        fields = ['eficacia', 'explicacion_eficacia', 'evidencia', 'seguimiento', 'fecha_implementacion']
        widgets = {
            'eficacia': forms.RadioSelect(),
            'explicacion_eficacia': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 3,
                'placeholder': 'Explicá por qué la OM resultó eficaz...'
            }),
            'evidencia': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Describí la evidencia de implementación...'}),
            'seguimiento': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Detalles del seguimiento realizado...'}),
            'fecha_implementacion': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['eficacia'].choices = [c for c in EficaciaOM.choices]
        self.fields['fecha_implementacion'].required = False
        self.fields['fecha_implementacion'].localize = False
        self.fields['fecha_implementacion'].widget.is_localized = False
        self.fields['fecha_implementacion'].widget.format = '%Y-%m-%d'

    def clean(self):
        cleaned = super().clean()
        eficacia = cleaned.get('eficacia')
        explicacion = (cleaned.get('explicacion_eficacia') or '').strip()
        if eficacia == EficaciaOM.EFICAZ and not explicacion:
            self.add_error('explicacion_eficacia', 'Ingresá la explicación de por qué fue eficaz.')
        return cleaned


class AdjuntoOMForm(forms.ModelForm):
    class Meta:
        model = AdjuntoOM
        fields = ['archivo']
        widgets = {
            'archivo': forms.FileInput(attrs={'class': 'form-input', 'accept': '.jpg,.jpeg,.png,.pdf,.xlsx,.xls'}),
        }
