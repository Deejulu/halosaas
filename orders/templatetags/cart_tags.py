from django import template

register = template.Library()

@register.filter
def first_value(d):
    """Return the first value from a dict_values or dict, or None if empty."""
    if hasattr(d, 'values'):
        v = list(d.values())
        return v[0] if v else None
    elif isinstance(d, dict):
        v = list(d.values())
        return v[0] if v else None
    elif isinstance(d, (list, tuple)):
        return d[0] if d else None
    return None
