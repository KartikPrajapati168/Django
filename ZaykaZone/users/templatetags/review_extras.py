# restaurants/templatetags/review_extras.py
from django import template

register = template.Library()

@register.filter
def times(number):
    """Repeat a range of numbers (for stars)"""
    return range(1, number + 1)
