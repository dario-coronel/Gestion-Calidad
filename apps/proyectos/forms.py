from django import forms
from .models import Proyecto, Subtarea


PRIORIDAD_CHOICES = [('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta')]


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = [
            'nombre', 'prioridad', 'responsable', 'fecha_inicio',
            'dias_ejecucion', 'proveedor', 'origen',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre del proyecto'}),
            'prioridad': forms.Select(attrs={'class': 'form-input'}),
            'responsable': forms.Select(attrs={'class': 'form-input'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'dias_ejecucion': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 30', 'min': 1}),
            'proveedor': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Proveedor externo o Interno'}),
            'origen': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.accounts.models import Usuario
        self.fields['responsable'].queryset = Usuario.objects.filter(is_active=True).order_by('first_name')
        self.fields['responsable'].empty_label = 'Seleccionar responsable...'


class SubtareaForm(forms.ModelForm):
    class Meta:
        model = Subtarea
        fields = ['descripcion']
        widgets = {
            'descripcion': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nueva tarea / hito...',
            }),
        }
