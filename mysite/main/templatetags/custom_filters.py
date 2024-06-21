from django import template

register = template.Library()

@register.filter(name='isinstance')
def isinstance_filter(value, class_name):
    return isinstance(value, class_name)