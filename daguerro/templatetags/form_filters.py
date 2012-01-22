import re
from django import template
from django.utils.safestring import mark_safe
register = template.Library()

@register.filter
def field_type(field, ftype):
    try:
        t = field.field.widget.__class__.__name__
        return t.lower() == ftype
    except:
        pass
    return False


@register.filter
def merge_attrs(field, attrs):
    regexp = re.compile('(.*)[ ]?class=\"(?P<class>.*)\".*')
    try:
        attrs = 'class="%s"' % " ".join([regexp.match(attrs).group(2), regexp.match(field.row_attrs).group(2)])
    except:
        pass
    return mark_safe(attrs)
    
