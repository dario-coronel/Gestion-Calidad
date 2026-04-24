from django import forms
from .models import NoConformidad, CincoPorques, AdjuntoNC


class NoConformidadForm(forms.ModelForm):
    class Meta:
        model = NoConformidad
        fields = [
            'fecha', 'area', 'responsable', 'id_muestra_lote',
            'parametro_afectado', 'descripcion', 'prioridad', 'clasificacion',
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'area': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Laboratorio de Suelos'}),
            'id_muestra_lote': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: SU-A342'}),
            'parametro_afectado': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Humedad %'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 4,
                                                  'placeholder': 'Describí el problema detectado...'}),
            'prioridad': forms.Select(attrs={'class': 'form-input'}),
            'clasificacion': forms.Select(attrs={'class': 'form-input'}),
            'responsable': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.accounts.models import Usuario
        self.fields['responsable'].queryset = Usuario.objects.filter(is_active=True).order_by('first_name')
        self.fields['responsable'].empty_label = 'Seleccionar responsable...'


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


class AdjuntoNCForm(forms.ModelForm):
    class Meta:
        model = AdjuntoNC
        fields = ['archivo']
        widgets = {
            'archivo': forms.FileInput(attrs={'class': 'form-input', 'accept': '.jpg,.jpeg,.png,.pdf,.xlsx,.xls'}),
        }
