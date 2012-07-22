import unicodedata


def normalize_unicode(s):
    return unicodedata.normalize('NFKD', s).encode('ascii','ignore')
