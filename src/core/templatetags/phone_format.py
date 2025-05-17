from django import template

register = template.Library()

PHONE_LEN_MOBILE = 11
PHONE_LEN_LANDLINE = 10


@register.filter
def format_phone(value):
    if not value:
        return ''
    digits = ''.join(filter(str.isdigit, str(value)))
    if len(digits) == PHONE_LEN_MOBILE:
        return f'({digits[:2]}) {digits[2]} {digits[3:7]}-{digits[7:]}'
    elif len(digits) == PHONE_LEN_LANDLINE:
        return f'({digits[:2]}) {digits[2:6]}-{digits[6:]}'
    else:
        return value
