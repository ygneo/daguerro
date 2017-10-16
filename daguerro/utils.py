from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.contrib.flatpages.models import FlatPage
from django.contrib.auth.models import User
from photologue.models import Gallery
from django import forms
import django_settings


def process_category_thread(request, slugs, urls_namespace='website', action=None):
    """
    Get a slugs string and add category thread to request.breadcrumbs.
    Also returns parent category slug and current category.
    If no Gallery object match slugs, raise HttpResponse404.
    """
    if slugs:
        request.breadcrumbs(_("Galeria"), reverse("%s-gallery" % urls_namespace))
        parent_slug = slugs.split('/')[-1]
        parent_categories, current_category = get_category_thread(slugs, urls_namespace)
        request.breadcrumbs(parent_categories)
    else:
        if action:
            request.breadcrumbs(_("Galeria"), reverse("%s-gallery" % urls_namespace))
        parent_slug = None
        current_category = None

    return parent_slug, current_category


def get_category_thread(slugs, urls_namespace):
    parent_categories = []
    current_category = None
    if slugs:
        i = 0
        list_slugs = slugs.split('/')
        for slug in list_slugs:
            i += 1
            category = get_object_or_404(Gallery, title_slug=slug)
            url = str(reverse("%s-gallery" % urls_namespace,
                              kwargs={"slugs": category.slugs_path()}))
            parent_categories.append((category.title, url))
        current_category = category

    return (parent_categories, current_category)


def daguerro_settings_to_dict():
    settings_dict = {}
    for setting in django_settings.models.Setting.objects.all():
        try:
            settings_dict[setting.name.lower()] = setting.setting_object.value
        except AttributeError:
            pass
    return settings_dict


def apply_batch_action(request):
    item_type = request.POST.get('item_type')
    action = request.POST.get('action')
    if request.method == 'POST' and item_type and action:
        if item_type == 'page':
            model = FlatPage
            attrs = {'registration_required': action == 'unpublish'}
        elif item_type == 'user':
            model = User
            attrs = {'is_active': action == 'activate'}
        ids = request.POST.getlist('%s[]' % item_type)
        objects = model.objects.filter(pk__in=ids)
        if action == 'delete':
            objects.delete()
        else:
            for obj in model.objects.filter(pk__in=ids):
                apply_action(request, obj, action, attrs)


def apply_action(request, obj, action, attrs):
    for attr, value in attrs.iteritems():
        setattr(obj, attr, value)
        obj.save()


class SettingField(forms.Field):

    def __init__(self, setting, *args , **kwargs):
        name = setting.name
        value = setting.setting_object.value
        if setting.setting_type == 'integer':
            return forms.IntegerField(initial=setting.setting_object.value,
                                       label=setting.name,
                                       )
