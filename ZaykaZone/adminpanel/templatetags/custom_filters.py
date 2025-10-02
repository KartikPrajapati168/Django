# adminpanel/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def div(value, arg):
    """
    Divides the value by the argument and returns the result.
    Handles division by zero and type errors gracefully.
    """
    try:
        return (float(value) / float(arg)) * 100  # Returns percentage
    except (ZeroDivisionError, ValueError, TypeError):
        return 0