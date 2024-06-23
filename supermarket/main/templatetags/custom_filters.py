from django import template

register = template.Library()

@register.filter
def dict_key(d, key):
    return d.get(key)


@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return float(value) * int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='get_value')
def get_value(dictionary, key):
    return dictionary.get(key)

@register.filter
def contains(value, arg):
    return arg.lower() in value.lower()