# -*- coding: utf-8 -*-
import os
import urllib
import logging
from django.utils.translation import ugettext as _
from django.conf import settings
from django import forms
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from photologue.models import Photo, PhotoSize
from form_utils.widgets import ImageWidget

logger = logging.getLogger(__name__)

class DaguerroPhotoWidget(ImageWidget):
    """ Simple extension to django-form-utils' ImageWidget providing templating when no image """ 

    template = """
               <div id="photo">
               %%(image)s
               </div>
               <div id="change-photo-fs">
               <label for="uploaded_photo">%(photo_label)s</label>
               %%(input)s
               </div>
              """

    class Media:
        js = (
            settings.STATIC_URL + '/daguerro/js/widgets/photo.js',
        )

    def __init__(self, photo_size,  *args, **kwargs):
        self.photo_size = photo_size
        ImageWidget.__init__(self, template=self.template, *args, **kwargs)

    def render(self, name, value, attrs=None):
        """
        Wrapper to super class render, providing a "no image" thumbnail when there's no picture,
        and getting the thumbnail image path if there's.
        """
        if not value:
            try:
                value = settings.DAG_NO_IMAGE[self.photo_size]
            except AttributeError:
                value = ''
        else: 
            if isinstance(value, long):
                try:
                    value = Photo.objects.get(pk=value).image
                except Photo.DoesNotExist:
                    value = None
            if value:
                path_dir = os.path.dirname(value.name)
                extension = os.path.basename(value.name).split('.')[-1]
                filename = smart_unicode(os.path.basename(value.name).replace('.%s' % extension, ''))
                value.name = "%s/cache/%s_%s.%s" % (path_dir, filename, self.photo_size, extension)
      	self.template = self.template % {'photo_label': _('Photo'),}
        return ImageWidget.render(self, name, value, attrs=attrs)


class DaguerroGalleryPhotoWidget(DaguerroPhotoWidget):
    """ Widget for gallery photo forms, providing upload and photo selection """ 

    template = '<div id="photo">%%(image)s</div>' \
               '<div id="change-photo-fs" class="box">' \
               '<input type="radio" name="photo_action" id="upload_new_photo" value="upload_new_photo" checked="checked"/>' \
               '<label for="uploaded_photo">' + _("Upload new photo") + '</label>' \
               '<input type="file" name="photo"/>' \
               '<input type="radio" name="photo_action" id="choose_photo" value="choose_photo"/>' \
               '<label for="photo_title">' + _("Search existing photo") + '</label>' \
               '<input type="text" name="photo_title" id="photo-title" class="inactive" value="'+ _("Write a photo title") +'"/>' \
               '<input type="hidden" name="id_photo"/>' \
               '<div id="photo_results" class="results"></div>' \
               '</div>'

    class Media:
        js = (
            settings.STATIC_URL + '/daguerro/js/widgets/photo.js',
        )


class DaguerroGalleryWidget(forms.Select):
    """ Custom Select widget showing one gallery item and a button to select another(s) """ 
    allow_multiple_selection = False

    class Media:
        js = (
            settings.STATIC_URL + '/daguerro/js/widgets/gallery.js',
        )

    def __init__(self, multiple, *args, **kwargs):
        self.allow_multiple_selection = multiple
        super(DaguerroGalleryWidget, self).__init__(*args, **kwargs)


class UserWidget(forms.TextInput):
    """ Custom widget showing a link to change password """
    template = '<a id="change_password" href="password/">' + _("Change pasword") + '</a>'

    def render(self, name, value, attrs=None):
        output = super(UserWidget, self).render(name, value, attrs)
        output += self.template
        return mark_safe(output)


class GoogleMapsWidget(forms.TextInput):
    """ A google maps searching and marking widget. 
        Actual lattitude and longitude are in a hidden input.
    """
    class Media:
        js = (
            'http://maps.google.com/maps/api/js?sensor=true',
            settings.STATIC_URL + '/daguerro/js/widgets/google_maps.js',
            )


    def render(self, name, value, attrs=None, choices=()):
        help_text = _('Write a location to be searched in the map. A marker will be drop in the map, and can be draggable.')
        no_results_text = _("No results. Try to do a different search that approaches to your target. If you don't want to use any location, click <a class='no_location'>here</a>.")
        no_location_text = _('No location')
        tooltip_title = _('Drag and drop this marker if you want to mark a different position in the map.')
        maps_html = """
                <span class="help_text">%(map_help)s</span>
                <div id="map_results" class="results"></div>
                <ul id="no_map_results" class="errorlist">
                <li>%(no_results_text)s</li>
                </ul>
                <div id="map_canvas" data-tooltip-title="%(tooltip_title)s"></div>
                """ % {'map_help': help_text,
                       'no_results_text': no_results_text,
                       'no_location_text': no_location_text,
                       'tooltip_title': tooltip_title}
        rendered = super(GoogleMapsWidget, self).render(name, value, attrs)
        return rendered + mark_safe(maps_html)


class WikipediaWidget(forms.TextInput):
    """ A wikipedia searching widget. 
        Actual wikipedia URL are in a hidden input passed as argument.
    """

    template = """
                <div class="ui-wikipedia-widget">
                <p class="ui-wikipedia-result-found">
                %(result_found_html)s
                <span class="ui-wikipedia-link-actions">
                %(link_text)s
                <a class="ui-wikipedia-link-yes" href="#">
                %(yes)s</a> /
                <a class="ui-wikipedia-link-no" href="#">
                %(no)s</a>
                </span>
                </p>
                <p class="ui-wikipedia-current-link">
                %(current_link_html)s
                <span class="ui-wikipedia-link-actions">
                <a class="ui-wikipedia-unlink" href="#">
                %(unlink)s</a>
                </span>
                </p>
               </div>                 
               <script>
                  $(document).ready(function () {
                     $("input[name=%(input_name)s]").wikipediaWidget({
                            insertAfter: "label[for=%(input_name)s]",
                            urlField: "%(url_field_id)s",
                     })
                  });
               </script>
              """

    result_found_html = _('Article found in wikipedia. ' \
                       '<a class="ui-wikipedia-link" href="#" target="_blank">' \
                       'Visit</a> | ')

    current_link_html = _('Linked to an article in wikipedia. ' \
                       '<a class="ui-wikipedia-link" href="#" target="_blank">' \
                       'Visit</a> | ')
    
    class Media:
        js = (
            settings.STATIC_URL + '/daguerro/js/widgets/wikipedia-widget.js',
            )
        css = {
            'screen': (settings.STATIC_URL + '/daguerro/css/widgets/wikipedia-widget.css',),
        }

    def __init__(self, url_field,  *args, **kwargs):
        self.url_field = url_field
        forms.TextInput.__init__(self, *args, **kwargs)


    def render(self, name, value, attrs=None, choices=()):
        rendered = super(WikipediaWidget, self).render(
            name, value, attrs)
        html = self.template % ({
            'input_name': name,
            'url_field_id': 'id_' + self.url_field,
            'result_found_html': self.result_found_html,
            'link_text': _("Link?"),
            'yes': _("Yes"),
            'no': _("No"),
            'current_link_html': self.current_link_html,
            'unlink': _("Unlink"),
        })
        return rendered + mark_safe(html)
