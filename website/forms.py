# -*- coding: utf-8 -*-
from django import forms
from form_utils.forms import BetterForm
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.conf import settings
from mptt.forms import TreeNodeMultipleChoiceField
from photologue.models import Gallery
from website.widgets import TreeCheckboxSelectMultipleWidget
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet
from custom_fields.forms import CustomFieldsMixin


class ShoppingCartForm(forms.Form):
    email = forms.EmailField(max_length=254)
    message = forms.CharField(required=False)


class SearchOptionsForm(BetterForm, SearchForm, CustomFieldsMixin):
    SEARCH_MODE_CHOICES = (
        ("TOTAL", _("Total match")),
        ("PARTIAL", _("Partial match")),
    )
    SEARCH_GALLERIES_CHOICES = (
        ("ALL", _('All galleries')),
        ("SELECTED", _('Only some galleries')),
    )
    title = forms.BooleanField(required=False, initial=True, label=_("Title"))
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
                                  'family', 'tags'],
                       'add_custom_fields': True,}
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


    def __init__(self, *args, **kwargs):
        super(SearchOptionsForm, self).__init__(*args, **kwargs)
        CustomFieldsMixin.__init__(self, model_name='Photo',
                                   FieldClass=forms.BooleanField,
                                   initial=settings.DAG_SEARCH_FIELDS_INITIAL
                                   )
        
    def clean(self):
        cleaned_data = self.cleaned_data
        checkable_fields = [cleaned_data[key] 
                            for key, field in self.fields.iteritems()
                            if isinstance(field, forms.BooleanField)]
        
        if not any(checkable_fields):
            raise forms.ValidationError(_("At least one of these checkboxes need to be checked:"))

        return cleaned_data

    def search(self):
        if not hasattr(self, "cleaned_data"):
            return self.no_query_found()
        
        search_fields = [key for key, value in self.cleaned_data.iteritems() if value == True]
        if 'title' not in search_fields:
            sqs = SearchQuerySet()
        else:
            sqs = super(SearchOptionsForm, self).search()
            # title is a document field and has been used for filtering in super method search()
            search_fields = [key for key in search_fields if key != 'title']

        query = sqs.query.clean(self.cleaned_data.pop('q'))
        galleries = [g.id for g in self.cleaned_data.get('galleries', [])]
        search_galleries = self.cleaned_data.get('search_galleries_choice', "ALL")

        query_words = query.split()
        for key in search_fields:
             if key == "tags":
                 sqs = sqs.filter_or(tags__in=[query.lower() for query in query_words])
             else:
                 sqs = self._filter_or_query_words(sqs, key, query_words)

        if search_galleries == 'SELECTED':
            sqs = sqs.filter_and(galleries_ids__in=galleries)
            
        return sqs
        
    
    def _filter_or_query_words(self, sqs, key, query_words):
        for word in query_words:
            sqs = sqs.filter_or(**{key: word})
        return sqs 

