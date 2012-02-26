from django import forms
from form_utils.forms import BetterForm
from django.utils.translation import ugettext as _

class ShoppingCartForm(forms.Form):
    pass


class SearchOptionsForm(BetterForm):
    title = forms.BooleanField(required=False, initial=True, label=_("Title"))
    alternative_title = forms.BooleanField(required=False, initial=True, label=_("Alternative title"))
    family = forms.BooleanField(required=False, initial=True, label=_("Family"))
    tags = forms.BooleanField(required=False, initial=True, label=_("Tags"),)
    caption = forms.BooleanField(required=False, initial=False, label=_("Caption"))
    location_title = forms.BooleanField(required=False, initial=False, label=_("Location"))
    galleries = forms.IntegerField(required=False, label=_("Galleries"))

    # Buscar en 
    # [] Titulo [] Nom cient [] Familia [] Etiquetas
    # [] Pie de foto  [] Localiz
    # Categorias 
    # [] 
    #   []
    
    class Meta:
        fields = ['title', 'alternative_title', 'family',
                  'caption', 'tags', 'location_title', 
                  'galleries']
        fieldsets = [('default-fields',
                      {'legend': _('Search in'),
                       'fields': ['title', 
                                  'alternative_title',
                                  'family', 'tags']}),
                     ('advanced-fields',
                      {'fields': ['caption', 
                                  'location_title']}),
                     ('galleries', 
                      {'fields': ['galleries']}),
                     ]
         
                      
    
                          
