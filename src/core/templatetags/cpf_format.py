from django import template

register = template.Library()


@register.filter
def format_cpf(cpf):
    if not cpf:
        return ''
    return cpf[:3] + '.' + cpf[3:6] + '.' + cpf[6:9] + '-' + cpf[9:11]
