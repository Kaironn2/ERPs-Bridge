from django import template

register = template.Library()


@register.simple_tag
def querystring_remove(request, key):
    dict_ = request.GET.copy()
    dict_.pop(key, None)
    return dict_.urlencode()
