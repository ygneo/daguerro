from django import forms
from django.contrib.flatpages.models import FlatPage
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import IntegrityError
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User, Group
from django.db.models import Q
from photologue.models import Photo, Gallery
from tinymce.widgets import TinyMCE
from form_utils.forms import BetterModelForm, BetterForm
from mptt.forms import TreeNodeMultipleChoiceField
from daguerro.widgets import DaguerroPhotoWidget, \
    DaguerroGalleryPhotoWidget, DaguerroGalleryWidget, \
    UserWidget, GoogleMapsWidget, WikipediaWidget
from custom_fields.forms import CustomFieldsModelForm
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet
from custom_fields.forms import CustomFieldsMixin
import django_settings
from daguerro.widgets import TreeCheckboxSelectMultipleWidget


class PhotoForm(CustomFieldsModelForm):
    image = forms.ImageField(
        label='',
        widget=DaguerroPhotoWidget(
            photo_size=settings.DAG_PHOTO_THUMB_SIZE_KEY,
            )
        )
    title_slug = forms.SlugField(
        widget=forms.widgets.HiddenInput,)
    alternative_title = forms.CharField(
        label=_("Alternative title"),
        widget=WikipediaWidget(
            url_field='alternative_title_url'),
        required=False)
    alternative_title_url = forms.URLField(
        widget=forms.widgets.HiddenInput, required=False)
    caption = forms.CharField(
        label=_("Caption"),
        widget=forms.Textarea(attrs={'rows':1,
                                     'cols':40}),
        required=False,)
    galleries = forms.ModelMultipleChoiceField(
        queryset=Gallery.objects.all(),
        widget=forms.widgets.SelectMultiple(
            attrs = {'size': 2}),
        label=_('Category(s)'),)
    location_title = forms.CharField(
        label=_('Location <a class="no_location">No location</a>'),
        widget=GoogleMapsWidget(
            attrs={'autocomplete': 'off',
                   'class': 'gmaps_location',
                   },
            ),
        required=False)
    latitude = forms.FloatField(widget=forms.HiddenInput(),
                               required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(),
                                required=False)

    class Meta:
        model = Photo
        fields = ['image', 'title', 'title_slug', 'galleries',
                  'is_public', 'caption', 'tags', 'location_title', 'latitude', 'longitude',]
        fieldsets = [('basic-metadata',
                      {'fields': ['title', 'title_slug',
                                  'is_public', 'caption',
                                  'alternative_title',
                                  'alternative_title_url',
                                  'family','galleries',
                                  'tags', 'location_title',
                                  'latitude', 'longitude',],
                       'legend': '',
                       'add_custom_fields': True}),
                     ('photo-area',
                      {'fields': ['image',], 'legend':''})]
        row_attrs = {'image': {'id': 'photo-related',
                               'class': 'visible'},
                     'is_public': {'class': 'inline'},
                     }

    def save(self, force_insert=False, force_update=False, commit=True):
        m = super(PhotoForm, self).save(commit = commit)
        if commit:
            self.instance.galleries = self.data.getlist('galleries')
            self.instance.save()
        return m


class GalleryForm(CustomFieldsModelForm):
    photo = forms.ImageField(
        label='',
        widget=DaguerroGalleryPhotoWidget(
            photo_size=settings.DAG_GALLERY_THUMB_SIZE_KEY,
            ),
        required=False)
    title = forms.CharField(label=_("Title"), required=True)
    title_slug = forms.SlugField(widget=forms.widgets.HiddenInput)
    parent = forms.ModelChoiceField(label=_("Parent category"),
                                    queryset=Gallery.objects.all(),
                                    empty_label=_("None"),
                                    widget=forms.Select(attrs = {'readonly':'readonly'}),
                                    required=False)
    description = forms.CharField(label=_("Description"),
                                  widget=forms.Textarea(attrs={'rows':1, 'cols':40}),
                                  required=False)

    class Meta:
        model = Gallery
        fields = ('photo', 'title', 'title_slug', 'is_public','description', 'parent')
        fieldsets = [('basic-metadata', {'fields':
                                         ['title', 'title_slug', 'is_public', 'description',
                                          'parent', 'tags'],
                                         'legend':'',
                                         'add_custom_fields': True
                                         }),
                     ('photo-area', {'fields': ['photo'], 'legend':''}),]
        row_attrs = {'photo': {'id': 'photo-related'}, 'is_public': {'class': 'inline'},}


    def clean_photo(self):
        cleaned_data = self.cleaned_data
        cleaned_data['id_photo'] = self.data['id_photo']
        photo = cleaned_data.get('photo')
        if isinstance(photo, long):
            try:
                cleaned_data['photo'] = Photo.objects.get(pk=photo)
            except Photo.DoesNotExist:
                raise forms.ValidationError(_('Photo does not exist'))
        elif isinstance(photo, InMemoryUploadedFile):
            new_photo = Photo(title=photo.name, image=photo, is_gallery_thumbnail=True)
            cleaned_data['photo'] = new_photo
            try:
                new_photo.save()
            except IntegrityError:
                new_photo.title = new_photo.get_avaliable_title()
                new_photo.save()
        return cleaned_data['photo']


    def save(self, force_insert=False, force_update=False, commit=True):
        if commit and self.cleaned_data['id_photo']:
            try:
                self.instance.photo = Photo.objects.get(pk=self.cleaned_data['id_photo'])
            except Photo.DoesNotExist:
                self.instance.photo = None
        m = super(GalleryForm, self).save(commit = commit)
        return m


class FlatPageForm(BetterModelForm):
    registration_required = forms.BooleanField(
        label = _("Public"),
        help_text = _('Public pages will be displayed in the website.'),
        required = False,
        # Representation is opposite of saved value
        widget = forms.CheckboxInput(check_test = lambda x: not x),
    )
    content = forms.CharField(
        widget=TinyMCE(
            attrs={
                'cols': 160,
                'rows': 30,
                'style': 'width: 100%',
                },
            ),
        label = _("Content"),
    )

    class Meta:
        model = FlatPage
        fields = ('title', 'registration_required', 'content',)
        row_attrs = {'registration_required': {'class': 'inline'},}


    def save(self, force_insert=False, force_update=False, commit=True):
        if self.instance:
            # Since representation is opposite to saved value
            self.instance.registration_required = not self.instance.registration_required
        m = super(FlatPageForm, self).save(commit = commit)
        return m


class UserForm(BetterModelForm):
    username = forms.CharField(
        widget = UserWidget(),
        label = _("Username"),
        help_text = None,
        required = False,
    )
    groups = forms.ModelMultipleChoiceField(
        queryset = Group.objects.all(),
        widget = forms.widgets.CheckboxSelectMultiple(),
        label = _("Groups"),
    )

    class Meta:
        model = User
        fields = ('username', 'is_active', 'first_name',
                  'last_name', 'email', 'groups',)
        row_attrs = {
            'is_active': {'class': 'inline'},
        }


class ResultListForm(forms.Form):

    def clean(self):
        user_id = self.data.get('user_id')
        if user_id:
            action = str(self.data['action'][0])
            item_type = str(self.data['item_type'][0])
            ids = map(lambda x: int(x),
                      self.data["%s[]" % item_type])
            unactivate_yourself = (
                action == 'unactivate' and \
                item_type == 'user' and \
                user_id in ids)
            if unactivate_yourself:
                raise forms.ValidationError(
                    _("You cannot unactivate your own user"))


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


class SettingsForm(BetterForm):
    dag_allow_photos_in_root_gallery = forms.BooleanField(
        label=_("dag_allow_photos_in_root_gallery"), required=False,
        )
    dag_results_per_page = forms.IntegerField(
        label=_("dag_results_per_page"), required=True,
        )
    dag_sales_email = forms.EmailField(
        label=_("dag_sales_email"), required=False,
        )
    dag_smtp_host = forms.URLField(
        label=_("dag_smtp_host"), required=False,
        )
    dag_smtp_host_user = forms.CharField(
        label=_("dag_smtp_host_user"), required=False,
        )
    dag_smtp_password = forms.CharField(
        label=_("dag_smtp_password"), required=False,
        )
    dag_confirmation_mail_subject = forms.CharField(
        label=_("dag_confirmation_mail_subject"), required=False,
        )


    class Meta:
        fields = ['dag_allow_photos_in_root_gallery', 'dag_results_per_page',
                  'dag_sales_email', 'dag_smtp_host', 'dag_smtp_host_user',
                  'dag_smtp_password', 'dag_confirmation_mail_subject',
                  ]
        fieldsets = [('basic', {'fields':
                                ['dag_allow_photos_in_root_gallery',
                                 'dag_results_per_page',
                                 ],
                                 'legend': _('Basic'),
                                }),
                     ('mailing', {'fields': ['dag_sales_email', 'dag_smtp_host',
                                             'dag_smtp_host_user', 'dag_smtp_password',
                                             'dag_confirmation_mail_subject',
                                             ],
                                  'legend':_('Mailing')}),]


    SETTING_TYPE = {'CharField': 'String',
                    'URLField': 'String',
                    'BooleanField': 'PositiveInteger',
                    'IntegerField': 'Integer',
                    'EmailField': 'Email',
                    }
    def save(self, commit=True):
        if commit:
            for key, value in self.cleaned_data.iteritems():
                field_type = self.fields[key].__class__.__name__
                django_settings.set(self.SETTING_TYPE[field_type], key.upper(), value)
