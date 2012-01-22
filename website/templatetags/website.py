from django import template
from django.conf import settings
from django.utils.encoding import force_unicode
import re

register = template.Library()


def numberformat(value):
    """
    Converts an integer to a string containing point every three digits.
    """
    orig = force_unicode(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>.\g<2>', orig)
    if orig == new:
        return new
    else:
        return numberformat(new)
numberformat.is_safe = True
register.filter(numberformat)
