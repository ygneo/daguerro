# -*- coding: utf-8 -*-
import os
import simplejson
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.http import HttpResponseRedirect
from photologue.models import Gallery, Photo
from daguerro.forms import PhotoForm, GalleryForm, FlatPageForm, UserForm, ResultListForm
from daguerro.context_processors import category_thread
from daguerro.utils import process_category_thread
from daguerro.shorcuts import redirect_to_gallery
from daguerro.models import DaguerroFlatPage
from daguerro.utils import apply_batch_action
from daguerro.paginator import DiggPaginator


@login_required
def index(request, slugs=None):
    # TODO This function is perfect for a request context processors reused
    # in gallery pages...
    parent_slug, current_category = process_category_thread(request, slugs, 'daguerro')
    categories = Gallery.objects.filter(parent__title_slug=parent_slug)
    photos = current_category.photos.all() if current_category else []
    
    user_groups = request.user.groups.all().values_list("name", flat=True)
    if 'Editor' in user_groups and len(user_groups) == 1:
        return HttpResponseRedirect(reverse("daguerro-pages-index"))
    
    page_no = int(request.GET.get('page', 1))
    paginator = DiggPaginator(photos, settings.DAG_RESULTS_PER_PAGE)
    return render_to_response('daguerro/gallery.html', 
                              {'categories': categories,
                               'current_category': current_category,
                               'photos_page': paginator.page(page_no),
                               'add_photo_in_root': settings.DAG_ADD_PHOTO_IN_ROOT,
                               'no_image_thumb_url': os.path.join(settings.STATIC_URL, settings.DAG_NO_IMAGE[settings.DAG_GALLERY_THUMB_SIZE_KEY]),
                               },
                              context_instance=RequestContext(request))


@login_required
def photo(request, action='add', slugs=None, slug=None):
    # TODO This function is perfect for a request context processors reused in gallery pages...
    parent_slug, current_category = process_category_thread(request, slugs, 'daguerro')
    
    if slug:
        current_action_title = _("Edit photography") 
        extra_context = {'current_action': 'edit'}
        photo = get_object_or_404(Photo, title_slug=slug)
        initial_galleries = photo.galleries.all().values_list('id', flat=True)
    else:
        current_action_title = _("Add photography") 
        extra_context = {'current_action': 'add'}
        photo = Photo()
        try:
            initial_galleries = [Gallery.objects.get(title_slug=parent_slug).id] 
        except Gallery.DoesNotExist:
            initial_galleries = None

    request.breadcrumbs(current_action_title, None)

    if request.method == 'POST': 
        # Force slugify, otherwise I need to fix photologue model or need client-side filling.
        request.POST['title_slug'] = slugify(request.POST['title'])
        form = PhotoForm(request.POST, request.FILES, instance=photo) 
        if form.is_valid(): 
            form.save()
            return redirect_to_gallery(slugs)
    else:
        form = PhotoForm(instance=photo, initial={'galleries': initial_galleries}) 

    return render_to_response('daguerro/photo.html', 
                              {'form': form,
                               'extra_context': extra_context,
                               'current_category': current_category,
                               'current_action_title': current_action_title,
                               'current_action': action, 
                               'no_image_thumb_url': os.path.join(settings.STATIC_URL, 
                                                     settings.DAG_NO_IMAGE[settings.DAG_PHOTO_THUMB_SIZE_KEY]),
                               },
                              context_instance=RequestContext(request))


@login_required
def photo_delete(request, slugs=None, id=None):
    photo = get_object_or_404(Photo, id=id)
    photo.delete()
    return redirect_to_gallery(slugs)


@login_required
def sort_items(request):
    item_type = request.POST.get('item_type', None)
    if request.method == 'POST' and item_type:
        if item_type == 'gallery':
            model = Gallery
        elif item_type == 'photo':
            model = Photo
        ids = request.POST.getlist('%s[]' % item_type)
        order = 0
        for id in ids:
            obj = get_object_or_404(model, id=id)
            obj.order = order
            obj.save()
            order += 1
    return HttpResponse(status=200)


@login_required
def gallery(request, action='add', slugs=""):
    # TODO This function is perfect for a request context processors reused in gallery pages...
    parent_slug, current_category = process_category_thread(request, slugs, 'daguerro', action)

    if action == 'edit':
        current_action_title = _("Edit Gallery") 
        parent_gallery = current_category.parent.id if current_category.parent else None
        gallery = get_object_or_404(Gallery, title_slug=current_category.title_slug)
    elif action == 'add':
        current_action_title = _("Add Gallery") 
        parent_gallery = current_category.id if current_category else None
        gallery = Gallery()

    request.breadcrumbs(current_action_title, None)

    if request.method == 'POST': 
        # Force slugify, otherwise I need to fix photologue model or need client-side filling.
        request.POST['title_slug'] = slugify(request.POST['title'])
        form = GalleryForm(request.POST, request.FILES, instance=gallery)
        if form.is_valid():
            form.save()
            return redirect_to_gallery(slugs, gallery, action)
    else:
        form = GalleryForm(instance=gallery, initial={'parent': parent_gallery})
        
    return render_to_response('daguerro/gallery_form.html', 
                              {'form': form,
                               'current_category': current_category,
                               'current_action_title': current_action_title,
                               'current_action': action, 
                               'no_image_thumb_url': os.path.join(settings.STATIC_URL, settings.DAG_NO_IMAGE['gallery']),
                               },
                              context_instance=RequestContext(request))


@login_required
def gallery_delete(request, slugs=None):
    parent_slug, current_category = process_category_thread(request, slugs, 'daguerro')    
    if current_category.parent:
        slugs = current_category.parent.slugs_path()
    else:
        slugs = None
    gallery = get_object_or_404(Gallery, id=current_category.id)
    gallery.delete()
    return redirect_to_gallery(slugs)


@login_required
def add_photo(request, gallery_id, photo_id):
    gallery = get_object_or_404(Gallery, id=gallery_id)
    photo = get_object_or_404(Photo, id=photo_id)
    photo.galleries = [gallery]
    photo.save()	
    return HttpResponse(status=200)


@login_required
def search_photo(request, format):
    term = request.GET.get('term', '')
    photos = Photo.objects.filter(title__icontains=term).order_by("title")
    if format == 'json':
        label = '<a><img src="%s"/><p>%s</p></a>' 
        response = HttpResponse(simplejson.dumps([{
                        'label': label % (p.get_thumbnail_url(), p.title),
                        'value': p.title,
                        'image': p.get_gallery_url(),
                        'id': p.id} for p in photos]))
    else:
        no_image_thumb_url = os.path.join(settings.STATIC_URL, settings.DAG_NO_IMAGE[settings.DAG_GALLERY_THUMB_SIZE_KEY])
        num_results = len(photos)
        response = render_to_response(
            'daguerro/gallery.html', {
                'categories': {},
                'current_category': None,                
                'photos': photos,
                'term': term,
                'num_results': num_results,
                'behaviour': 'search_results',
                'add_photo_in_root': settings.DAG_ADD_PHOTO_IN_ROOT,
                'no_image_thumb_url': no_image_thumb_url,},
            context_instance=RequestContext(request))
    return response


@login_required
def pages_index(request):
    if request.method == 'POST':
        form = ResultListForm(request.POST)
        if form.is_valid():
            apply_batch_action(request)
    return render_to_response(
        'daguerro/pages.html', {
            'form': ResultListForm(),
            'pages': DaguerroFlatPage.objects.all(),
            'current_action': 'pages',
            },
        context_instance=RequestContext(request))
    
    
@login_required
def page(request, action, id=None):
    if action == 'edit':
        current_action_title = _("Edit Page") 
        page = get_object_or_404(DaguerroFlatPage, pk=id)
    elif action == 'add':
        current_action_title = _("Add Page") 
        page = DaguerroFlatPage(registration_required=True)

    request.breadcrumbs((
            (_("Pages"), reverse("daguerro-pages-index")),
            (current_action_title, None),
    ))

    if request.method == 'POST': 
        form = FlatPageForm(request.POST, instance=page) 
        if form.is_valid(): 
            form.save()
            return HttpResponseRedirect(reverse("daguerro-pages-index"))
    else:
        form = FlatPageForm(instance=page)

    return render_to_response('daguerro/page_form.html', 
                              {'form': form,
                               'current_action_title': current_action_title,
                               'current_action': action, 
                               },
                              context_instance=RequestContext(request))


@login_required
def users_index(request):
    if request.method == 'POST':
        data = dict(request.POST)
        data.update(user_id = request.user.pk)
        form = ResultListForm(data) 
        if form.is_valid():
            apply_batch_action(request)
    else:
        form = ResultListForm()
    return render_to_response(
        'daguerro/users.html', {
            'form': form,
            'users': User.objects.filter(is_superuser=False),
            'current_action': 'users',
            },
        context_instance=RequestContext(request))


@login_required
def user(request, action, id=None):
    if action == 'edit':
        current_action_title = _("Edit User") 
        user = get_object_or_404(User, pk=id)
        Form = UserForm
    elif action == 'add':
        current_action_title = _("Add User") 
        user = User()
        Form = UserCreationForm

    request.breadcrumbs((
            (_("Users"), reverse("daguerro-users-index")),
            (current_action_title, None),
    ))

    if request.method == 'POST': 
        form = Form(request.POST, instance=user) 
        if form.is_valid(): 
            form.save()
            if action == 'add':
                url = reverse("daguerro-user", 
                              args=[form.instance.pk])
            else:
                url = reverse("daguerro-users-index")
            return HttpResponseRedirect(url)
    else:
        form = Form(instance=user)

    return render_to_response('daguerro/user_form.html', 
                              {'form': form,
                               'current_action_title': current_action_title,
                               'current_action': action, 
                               },
                              context_instance=RequestContext(request))


@login_required
def user_change_password(request, id):
    current_action_title = _("Change password") 
    action = "change_password"
    user = get_object_or_404(User, pk=id)

    request.breadcrumbs((
            ("Users", reverse("daguerro-users-index")),
            (current_action_title, None),
    ))
    if request.method == 'POST': 
        form = SetPasswordForm(user, request.POST) 
        if form.is_valid(): 
            form.save()
            return HttpResponseRedirect(reverse("daguerro-user", 
                                                args=[user.pk]))
    else:
        form = SetPasswordForm(user)

    return render_to_response('daguerro/user_form.html', 
                              {'form': form,
                               'current_action_title': current_action_title,
                               'current_action': action, 
                               },
                              context_instance=RequestContext(request))
