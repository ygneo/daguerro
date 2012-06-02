# -*- coding: utf-8 -*-
from django import forms
from form_utils.forms import BetterForm
from django.utils.translation import ugettext as _
from django.db.models import Q
from mptt.forms import TreeNodeMultipleChoiceField
from photologue.models import Gallery
from website.widgets import TreeCheckboxSelectMultipleWidget
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet

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
        queryset=Gallery.objects.filter(is_public=True), 
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
                     ('galleries-fields', 
                      {'fields': ['search_galleries_choice',
                                  'galleries',
                                  ],
                       }
                      ),
                     ]

    
    def clean(self):
        cleaned_data = self.cleaned_data
        checkable_fields = [cleaned_data['title'], cleaned_data['alternative_title'],
                            cleaned_data['family'], cleaned_data['caption'],
                            cleaned_data['tags'], cleaned_data['location_title'],
                            ]
        if not any(checkable_fields):
            raise forms.ValidationError(_("At least one of these checkboxes need to be checked:"))

        # Always return the full collection of cleaned data.
        return cleaned_data

    def search(self):
        if not hasattr(self, "cleaned_data"):
            return self.no_query_found()
        
        search_fields = [key for key, value in self.cleaned_data.iteritems() if value == True]
        if 'title' not in search_fields:
            sqs = SearchQuerySet()
        else:
            sqs = super(SearchOptionsForm, self).search()
        query = self.cleaned_data.pop('q')
        galleries = [g.id for g in self.cleaned_data.get('galleries', [])]
        search_galleries = self.cleaned_data.get('search_galleries_choice', "ALL")

        # TODO filter out the document field
        for key in search_fields:
            sqs = sqs.filter_or(**{key: sqs.query.clean(query)})
            if key == "tags":
                sqs = sqs.filter_or(tags__in=[sqs.query.clean(query.lower()).split(" ")])

        if search_galleries == 'SELECTED':
            sqs = sqs.filter_and(galleries__in=galleries)
            
        return sqs
        
        
