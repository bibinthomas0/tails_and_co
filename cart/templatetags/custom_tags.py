from django import template

register = template.Library()

@register.filter
def intmul(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0
