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

@register.filter
def get_item(list_obj, index):
    """Get item from list by index"""
    try:
        return list_obj[int(index)]
    except (IndexError, ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide value by arg"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter
def mul(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0