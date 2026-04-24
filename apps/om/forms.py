from django import forms
from .models import OportunidadMejora, AdjuntoOM


class OportunidadMejoraForm(forms.ModelForm):
    class Meta:
        model = OportunidadMejora
        fields = [
            'fecha', 'sector', 'responsable', 'clasificacion',
            'descripcion', 'beneficio_potencial',
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'sector': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Producción / Laboratorio'}),
            'clasificacion': forms.Select(attrs={'class': 'form-input'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Describí la oportunidad o sugerencia de mejora...'}),
            'beneficio_potencial': forms.Select(attrs={'class': 'form-input'}),
            'responsable': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.accounts.models import Usuario
        self.fields['responsable'].queryset = Usuario.objects.filter(is_active=True).order_by('first_name')
        self.fields['responsable'].empty_label = 'Seleccionar responsable...'


class AdjuntoOMForm(forms.ModelForm):
    class Meta:
        model = AdjuntoOM
        fields = ['archivo']
        widgets = {
            'archivo': forms.FileInput(attrs={'class': 'form-input', 'accept': '.jpg,.jpeg,.png,.pdf,.xlsx,.xls'}),
        }
