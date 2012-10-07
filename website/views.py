#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.core.mail import BadHeaderError
from django.template import Context
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from photologue.models import Photo
from daguerro.utils import process_category_thread
from daguerro.paginator import DiggPaginator
from daguerro.forms import SearchOptionsForm
from website.forms import ShoppingCartForm


def gallery(request, slugs=None):
    parent_slug, current_gallery = process_category_thread(request, slugs)
    no_image_thumb_url = os.path.join(settings.STATIC_URL, 
                                          settings.DAG_NO_IMAGE[settings.DAG_GALLERY_THUMB_SIZE_KEY])
    
    # TODO Find a better way to do this (parent by default for a category, i.e. root)
    if current_gallery:
        children_galleries = current_gallery.get_children().filter(is_public=True)
        brother_galleries = current_gallery.get_siblings(include_self=True).filter(is_public=True)
        photos = current_gallery.photos.public()
        if current_gallery.photos_ordering:
            photos = photos.order_by(current_gallery.photos_ordering)
    else:
        brother_galleries = None
        children_galleries = None
        photos = Photo.objects.public().orphans()
    
    page_no = int(request.GET.get('page', 1))
    paginator = DiggPaginator(photos, settings.DAG_RESULTS_PER_PAGE)
    template = 'website/gallery.html' if slugs else 'website/index.html'  
    return render_to_response(template, {'gallery': current_gallery, 
                                         'brother_galleries': brother_galleries, 
                                         'children_galleries': children_galleries,
                                         'search_options_form': SearchOptionsForm(),
                                         'no_image_thumb_url': no_image_thumb_url,
                                         'photos_page': paginator.page(page_no),
                                         }, context_instance=RequestContext(request)
                              )


def photo(request, gallery_slugs, photo_slug):
    parent_slug, current_gallery = process_category_thread(request, gallery_slugs)
    parent_category = current_gallery.parent
    
    try:
        photo = Photo.objects.get(title_slug=photo_slug)
    except Photo.DoesNotExist:
        raise Http404
    custom_fields = photo.custom_fields.exclude(value='')
    
    return render_to_response('website/photo.html', {
            'photo': photo,
            'custom_fields': custom_fields,
            'parent_category': parent_category,
            'gallery_slugs': gallery_slugs,
            'search_options_form': SearchOptionsForm(),
            }, context_instance=RequestContext(request))


def send_request_photos(request):
    form = ShoppingCartForm(request.POST)
    if request.method == 'POST' : 
        form = ShoppingCartForm(request.POST)
        
        if form.is_valid():
            subject = "[Barres Fotonatura] Solicitud de fotografías"
            message = request.POST.get("message", "")
            sender_email = request.POST.get("email", "")
            photo_items = request.POST.getlist("shopping-cart-items[]")
            redirect_to_url = request.POST.get("redirect_to_url", "/")
            _send_request_emails(subject, message, sender_email, photo_items)
            response = HttpResponseRedirect(redirect_to_url)
            response.delete_cookie(settings.DAGUERRO_CART_SESSION_KEY)
            return response
        else:
            return HttpResponseBadRequest(form.errors)
    else: 
        return HttpResponseBadRequest("POST only")


def _send_request_emails(subject, message, sender_email, photo_items):
    try:
        t = get_template('website/request_photos_mail.html')
        photos = Photo.objects.filter(pk__in=photo_items)
        no_image_thumb_url = os.path.join(settings.STATIC_URL, settings.DAG_NO_IMAGE[settings.DAG_GALLERY_THUMB_SIZE_KEY])
        body = t.render(Context({'photos': photos, 
                                 'sender_email': sender_email,
                                 'message': message, 
                                 'no_image_thumb_url': no_image_thumb_url}
                                ))
        _send_html_mail(EmailMultiAlternatives(subject, 
                                               body, 
                                               settings.EMAIL_HOST_USER,
                                               [settings.EMAIL_HOST_USER],)
                        )
        _send_html_mail(EmailMultiAlternatives("[Barres Fotonatura] Pedido enviado", 
                                               settings.DAGUERRO_EMAIL_BODY,
                                               settings.EMAIL_HOST_USER,
                                               [sender_email],)
                        )
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
 

def _send_html_mail(msg):
    msg.attach_alternative(msg.body, "text/html")            
    msg.send()

