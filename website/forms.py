# -*- coding: utf-8 -*-
from django import forms
from form_utils.forms import BetterForm
from django.utils.translation import ugettext as _
from mptt.forms import TreeNodeMultipleChoiceField
from photologue.models import Gallery
from website.widgets import TreeCheckboxSelectMultipleWidget
from haystack.forms import SearchForm


class ShoppingCartForm(forms.Form):
    pass


class SearchOptionsForm(BetterForm, SearchForm):
    SEARCH_MODE_CHOICES = (
        ("TOTAL", _("Total match")),
        ("PARTIAL", _("Partial match")),
    )
    SEARCH_GALLERIES_CHOICES = (
        ("ALL", _('All galleries')),
        ("SELECTED", _('Only some galleries')),
    )
    title = forms.BooleanField(required=False, initial=True, label=_("Title"))
    alternative_title = forms.BooleanField(required=False, initial=True, 
                                           label=_("Alternative title"))
    family = forms.BooleanField(required=False, initial=True, label=_("Family"))
    tags = forms.BooleanField(required=False, initial=True, label=_("Tags"),)
    caption = forms.BooleanField(required=False, initial=False, label=_("Caption"))
    location_title = forms.BooleanField(required=False, initial=False, label=_("Location"))
    search_galleries_choice = forms.ChoiceField(choices=SEARCH_GALLERIES_CHOICES, 
                                                widget=forms.RadioSelect(attrs={'id': 'search_in_galleries'}),
                                                initial="ALL",
                                                label="",)
    galleries = TreeNodeMultipleChoiceField(
        required=False,
        queryset=Gallery.objects.all(), 
        label=_("Galleries"),
        widget = TreeCheckboxSelectMultipleWidget(attrs = {'id': 'galleries'}, 
                                                  show_empty_choices=False),
        level_indicator=u'-'
        )
   
    class Meta:
        fields = ['title', 'alternative_title', 'family',
                  'caption', 'tags', 'location_title', 
                  'search_galleries_choice', 'galleries',]
        
        fieldsets = [('default-fields',
                      {'fields': ['title', 
                                  'alternative_title',
                                  'family', 'tags']}
                      ),
                     ('advanced-fields',
                      {'fields': ['caption', 
                                  'location_title',
                                  ]}
                      ),
                     ('galleries', 
                      {'fields': ['search_galleries_choice',
                                  'galleries',
                                  ],
                       }
                      ),
                     ]

    def clean(self):
        cleaned_data = super(SearchOptionsForm, self).clean()
        return cleaned_data


    def search(self):
        sqs = super(SearchOptionsForm, self).search()
        return sqs
        
        
