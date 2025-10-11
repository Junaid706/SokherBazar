from django import template

register = template.Library()

@register.filter
def times(value):
    try:
        return range(int(value))
    except:
        return range(0)




@register.filter
def to_int(value):
    """Converts a value to integer"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

