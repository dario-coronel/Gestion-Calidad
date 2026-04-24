from django import template

register = template.Library()


@register.filter
def get_item(obj, key):
    """Accede a dict['key'] o obj.key según el tipo."""
    if isinstance(obj, dict):
        return obj.get(key, '')
    return getattr(obj, key, '')


@register.filter
def get_form_field(form, field_name):
    """Renderiza un campo de formulario por nombre: form|get_form_field:'campo'"""
    return form[field_name]
