from django import template

register = template.Library()

@register.filter
def verbose(model, field):
    return model._meta.get_field(field).verbose_name

@register.filter
def base_url(i18n_url):
    return '/' + i18n_url.split('/', maxsplit=2)[-1]