from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Permite acceder a un dict con una variable en template: dict|get_item:variable"""
    return dictionary.get(key, '')


@register.filter
def get_form_field(form, field_name):
    """Renderiza un campo de formulario por nombre: form|get_form_field:'campo'"""
    return form[field_name]
