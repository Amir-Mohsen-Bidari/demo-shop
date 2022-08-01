from django import template

register = template.Library()

@register.filter
def verbose(model, field):
    return model._meta.get_field(field).verbose_name