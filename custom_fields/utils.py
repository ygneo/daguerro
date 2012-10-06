import unicodedata


def safe_custom_field_name(s):
    s = unicodedata.normalize('NFKD', unicode(s)).encode('ascii','ignore').lower()
    return s.lstrip().rstrip().replace(" ", "_")
    
