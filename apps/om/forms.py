from django import forms
from .models import OportunidadMejora, AdjuntoOM, EficaciaOM


class OportunidadMejoraForm(forms.ModelForm):
    class Meta:
        model = OportunidadMejora
        fields = [
            'fecha', 'sector', 'responsable', 'clasificacion',
            'descripcion', 'problema_a_mejorar', 'beneficio_potencial',
            'rango_evaluacion',
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'sector': forms.Select(attrs={'class': 'form-input'}),
            'clasificacion': forms.Select(attrs={'class': 'form-input'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Describí la oportunidad o sugerencia de mejora...'}),
            'problema_a_mejorar': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Describí el problema o área a mejorar...'}),
            'beneficio_potencial': forms.Select(attrs={'class': 'form-input'}),
            'responsable': forms.Select(attrs={'class': 'form-input'}),
            'rango_evaluacion': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.accounts.models import Usuario
        from apps.core.models import Sector
        self.fields['sector'].queryset = Sector.objects.filter(activo=True).order_by('nombre')
        self.fields['sector'].empty_label = 'Seleccionar sector...'
        self.fields['sector'].required = False
        self.fields['responsable'].queryset = Usuario.objects.filter(is_active=True).order_by('first_name')
        self.fields['responsable'].empty_label = 'Seleccionar responsable...'
        self.fields['rango_evaluacion'].empty_label = 'Sin definir'


class EficaciaOMForm(forms.ModelForm):
    class Meta:
        model = OportunidadMejora
        fields = ['eficacia', 'evidencia', 'seguimiento', 'fecha_implementacion']
        widgets = {
            'eficacia': forms.RadioSelect(),
            'evidencia': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Describí la evidencia de implementación...'}),
            'seguimiento': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Detalles del seguimiento realizado...'}),
            'fecha_implementacion': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['eficacia'].choices = [c for c in EficaciaOM.choices]
        self.fields['fecha_implementacion'].required = False


class AdjuntoOMForm(forms.ModelForm):
    class Meta:
        model = AdjuntoOM
        fields = ['archivo']
        widgets = {
            'archivo': forms.FileInput(attrs={'class': 'form-input', 'accept': '.jpg,.jpeg,.png,.pdf,.xlsx,.xls'}),
        }
