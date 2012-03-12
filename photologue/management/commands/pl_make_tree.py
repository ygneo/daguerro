from mptt.models import MPTTModelBase
from django.core.management.base import BaseCommand, CommandError
from photologue.models import Gallery

class Command(BaseCommand):
    help = ('Migrate existing galleries to MPTT structure')

    requires_model_validation = True

    def handle(self, *args, **options):
        if type(Gallery) != MPTTModelBase:
            CommandError("Gallery must be subclass of MPTTModelBase")
        
        Gallery.objects.rebuild()
        

