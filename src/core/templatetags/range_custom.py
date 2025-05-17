from django import template

register = template.Library()


@register.filter
def range_custom(value, arg):
    return range(int(value), int(arg) + 1)
