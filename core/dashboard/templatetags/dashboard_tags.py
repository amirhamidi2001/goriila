from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    دسترسی به مقادیر dictionary در Template

    استفاده:
    {{ dictionary|get_item:key }}
    """
    if dictionary:
        return dictionary.get(key)
    return None


@register.filter
def mul(value, arg):
    """
    ضرب دو عدد در Template

    استفاده:
    {{ value|mul:arg }}
    """
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0
