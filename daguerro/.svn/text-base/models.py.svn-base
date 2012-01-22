from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.db import models

class DaguerroFlatPage(FlatPage):
    class Meta:
        proxy = True

    def save(self):
        self.url = '/%s/' % slugify(self.title)
        super(DaguerroFlatPage, self).save()
        self.sites = [Site.objects.get(pk=settings.SITE_ID)]
        super(DaguerroFlatPage, self).save()
