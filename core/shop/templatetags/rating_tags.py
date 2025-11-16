from django import template

register = template.Library()

@register.filter
def star_parts(value):
    """
    Returns lists for full, half, and empty stars.
    """
    try:
        value = float(value)
    except:
        value = 0

    full = int(value)
    half = 1 if value - full >= 0.5 else 0
    empty = 5 - full - half

    return {
        "full": range(full),
        "half": range(half),
        "empty": range(empty),
    }
