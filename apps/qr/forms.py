from django import forms
from .models import QuejaReclamo, AdjuntoQR


class QuejaReclamoForm(forms.ModelForm):
    class Meta:
        model = QuejaReclamo
        fields = [
            'fecha', 'area_origen', 'responsable', 'id_cliente_pedido',
            'tipo_reclamo', 'descripcion', 'prioridad', 'clasificacion',
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'area_origen': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Ventas / Despacho'}),
            'id_cliente_pedido': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: CLI-001 / PED-2026-042'}),
            'tipo_reclamo': forms.Select(attrs={'class': 'form-input'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Describí el reclamo del cliente...'}),
            'prioridad': forms.Select(attrs={'class': 'form-input'}),
            'clasificacion': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Clasificación adicional (opcional)'}),
            'responsable': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.accounts.models import Usuario
        self.fields['responsable'].queryset = Usuario.objects.filter(is_active=True).order_by('first_name')
        self.fields['responsable'].empty_label = 'Seleccionar responsable...'


class AdjuntoQRForm(forms.ModelForm):
    class Meta:
        model = AdjuntoQR
        fields = ['archivo']
        widgets = {
            'archivo': forms.FileInput(attrs={'class': 'form-input', 'accept': '.jpg,.jpeg,.png,.pdf,.xlsx,.xls'}),
        }
