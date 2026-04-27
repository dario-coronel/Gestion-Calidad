from django import forms
from .models import QuejaReclamo, AdjuntoQR


class QuejaReclamoForm(forms.ModelForm):
    class Meta:
        model = QuejaReclamo
        fields = [
            'fecha', 'sector', 'responsable', 'id_cliente_pedido',
            'tipo_reclamo', 'descripcion', 'prioridad', 'clasificacion',
            'dias_resolucion', 'quien_recibe', 'detalle_visita_cliente',
            'acciones_a_tomar', 'resultado', 'envio_mail', 'fecha_cierre',
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'sector': forms.Select(attrs={'class': 'form-input'}),
            'id_cliente_pedido': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: CLI-001 / PED-2026-042'}),
            'tipo_reclamo': forms.Select(attrs={'class': 'form-input'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Describí el reclamo del cliente...'}),
            'prioridad': forms.Select(attrs={'class': 'form-input'}),
            'clasificacion': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Clasificación adicional (opcional)'}),
            'responsable': forms.Select(attrs={'class': 'form-input'}),
            'dias_resolucion': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 5', 'min': 1}),
            'quien_recibe': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre de quien recibe la queja'}),
            'detalle_visita_cliente': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Detallá la visita o contacto con el cliente...'}),
            'acciones_a_tomar': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Describí las acciones acordadas...'}),
            'resultado': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Resultado final de la gestión...'}),
            'envio_mail': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-teal-600 border-gray-300 rounded'}),
            'fecha_cierre': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
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
        self.fields['dias_resolucion'].label = 'Tiempo de respuesta (días)'
        self.fields['fecha_cierre'].required = False


class AdjuntoQRForm(forms.ModelForm):
    class Meta:
        model = AdjuntoQR
        fields = ['archivo']
        widgets = {
            'archivo': forms.FileInput(attrs={'class': 'form-input', 'accept': '.jpg,.jpeg,.png,.pdf,.xlsx,.xls'}),
        }
