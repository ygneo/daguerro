from django import forms
from form_utils.forms import BetterForm
from django.utils.translation import ugettext as _
from mptt.forms import TreeNodeMultipleChoiceField
from photologue.models import Gallery
from website.widgets import TreeCheckboxSelectMultipleWidget

class ShoppingCartForm(forms.Form):
    pass


class SearchOptionsForm(BetterForm):
    title = forms.BooleanField(required=False, initial=True, label=_("Title"))
    alternative_title = forms.BooleanField(required=False, initial=True, label=_("Alternative title"))
    family = forms.BooleanField(required=False, initial=True, label=_("Family"))
    tags = forms.BooleanField(required=False, initial=True, label=_("Tags"),)
    caption = forms.BooleanField(required=False, initial=False, label=_("Caption"))
    location_title = forms.BooleanField(required=False, initial=False, label=_("Location"))
    galleries = TreeNodeMultipleChoiceField(
        queryset=Gallery.objects.all(), 
        label=_("Galleries"),
        widget = TreeCheckboxSelectMultipleWidget(attrs = {'id': 'galleries'}),
        level_indicator=u'-'
        )
    
    class Meta:
        fields = ['title', 'alternative_title', 'family',
                  'caption', 'tags', 'location_title', 
                  'galleries']
        fieldsets = [('default-fields',
                      { 'fields': ['title', 
                                   'alternative_title',
                                   'family', 'tags']}),
                     ('advanced-fields',
                      {'fields': ['caption', 
                                  'location_title',
                                  ]}),
                     ('galleries', 
                      {'fields': ['galleries'
                                  ],
                       }
                      ),
                     ]
         
                      
                          
