from django import forms
from .models import VerificacionEficacia


class VerificacionForm(forms.ModelForm):
    class Meta:
        model = VerificacionEficacia
        fields = ['responsable', 'fecha_realizada', 'estado', 'resultado_descripcion', 'evidencia']
        widgets = {
            'responsable': forms.Select(attrs={'class': 'form-input'}),
            'fecha_realizada': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'estado': forms.Select(attrs={'class': 'form-input'}),
            'resultado_descripcion': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 4,
                'placeholder': 'Describí los resultados observados durante la verificación...',
            }),
            'evidencia': forms.FileInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.accounts.models import Usuario
        self.fields['responsable'].queryset = Usuario.objects.filter(is_active=True).order_by('first_name')
        self.fields['responsable'].empty_label = 'Seleccionar responsable...'
