from django import forms
from .models import VerificacionEficacia


class VerificacionForm(forms.ModelForm):
    class Meta:
        model = VerificacionEficacia
        fields = ['responsable', 'fecha_realizada', 'estado', 'resultado_descripcion', 'evidencia']
        widgets = {
            'responsable': forms.Select(attrs={'class': 'form-input'}),
            'fecha_realizada': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-input'}),
            'estado': forms.Select(attrs={'class': 'form-input'}),
            'resultado_descripcion': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 4,
                'placeholder': 'Describí los resultados observados durante la verificación...',
            }),
            'evidencia': forms.FileInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.core.models import Responsable
        self.fields['responsable'].queryset = Responsable.objects.filter(activo=True).order_by('nombre')
        self.fields['responsable'].empty_label = 'Seleccionar responsable...'
        self.fields['fecha_realizada'].localize = False
        self.fields['fecha_realizada'].widget.is_localized = False
        self.fields['fecha_realizada'].widget.format = '%Y-%m-%d'
