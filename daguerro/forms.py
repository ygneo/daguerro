from django import forms
from django.contrib.flatpages.models import FlatPage
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import IntegrityError
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User, Group
from photologue.models import Photo, Gallery
from tinymce.widgets import TinyMCE
from form_utils.forms import BetterModelForm
from daguerro.widgets import DaguerroPhotoWidget, \
    DaguerroGalleryPhotoWidget, DaguerroGalleryWidget, \
    UserWidget, GoogleMapsWidget, WikipediaWidget


class PhotoForm(BetterModelForm):
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
        widget=WikipediaWidget(url_field='alternative_title_url'),
        required=False)
    alternative_title_url = forms.URLField(widget=forms.widgets.HiddenInput, required=False)
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
        fields = ['image', 'title', 'title_slug', 'galleries', 'alternative_title', 'alternative_title_url', 'family', 
                  'is_public', 'caption', 'tags', 'location_title', 'latitude', 'longitude',]
        fieldsets = [('basic-metadata', 
                      {'fields': ['title', 'title_slug', 
                                  'is_public', 'caption', 
                                  'alternative_title', 
                                  'alternative_title_url', 
                                  'family','galleries', 
                                  'tags', 'location_title',
                                  'latitude', 'longitude',],
                       'legend': '',}),
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


class GalleryForm(BetterModelForm):
    photo = forms.ImageField(
        label='', 
        widget=DaguerroGalleryPhotoWidget(
            photo_size=settings.DAG_GALLERY_THUMB_SIZE_KEY, 
            ),
        required=False)
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
                                         'legend':''}),
                     ('photo-area', {'fields': ['photo'], 'legend':''}),]
        row_attrs = {'photo': {'id': 'photo-related'}, 'is_public': {'class': 'inline'},}
        

    # def clean(self):
    #     cleaned_data = self.cleaned_data
    #     cleaned_data['id_photo'] = self.data['id_photo']
    #     photo = cleaned_data.get('photo')
    #     if isinstance(photo, long): 
    #         try: 
    #             cleaned_data['photo'] = Photo.objects.get(pk=photo)
    #         except Photo.DoesNotExist:
    #             raise forms.ValidationError(_('Photo does not exist'))
    #     elif isinstance(photo, InMemoryUploadedFile) and 'title' in cleaned_data:
    #         print "IS IN MEMORY"
    #         new_photo = Photo(title=cleaned_data['title'], image=photo)
    #         cleaned_data['photo'] = new_photo
    #         if self.instance:
    #             try:
    #                 new_photo.save()
    #             except IntegrityError:
    #                 new_photo.title = new_photo.get_avaliable_title()
    #                 new_photo.save()
    #             self.instance.photo = new_photo        
        
    #     return cleaned_data

    
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
            new_photo = Photo(title=photo.name, image=photo)
            cleaned_data['photo'] = new_photo
            try:
                new_photo.save()
            except IntegrityError:
                new_photo.title = new_photo.get_avaliable_title()
                new_photo.save()            
        return cleaned_data['photo']
       
    
    def clean_title(self):
        title = self.cleaned_data['title']
        if not hasattr(self.instance, "id") and Gallery.objects.filter(title=title).count():
            raise forms.ValidationError(_('A gallery samed titled already exists.'))
        return title
        

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
                    _("You cannot unactivate your own user")                )
