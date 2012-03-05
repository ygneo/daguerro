from django import forms
from django.conf import settings

class SearchGalleryWidget(forms.ModelMultipleChoiceField):
    allow_multiple_selection = True

    class Media:
        js = (
            settings.STATIC_URL + '/daguerro/js/widgets/search.js',
        )

    def __init__(self, *args, **kwargs):
        super(SearchGalleryWidget, self).__init__(*args, **kwargs)
