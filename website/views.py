#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from django.template import Context, Template
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives, EmailMessage

from photologue.models import Gallery, Photo
from daguerro.utils import process_category_thread
from website.forms import ShoppingCartForm, SearchOptionsForm


def gallery(request, slugs=None):
    parent_slug, current_gallery = process_category_thread(request, slugs)
    
    # TODO Find a better way to do this (parent by default for a category, i.e. root)
    if current_gallery and current_gallery.parent:
        brother_galleries = Gallery.objects.public().filter(parent=current_gallery.parent)
    else:
        brother_galleries = None
    
    template = 'website/gallery.html' if slugs else 'website/index.html'    
    return render_to_response(template, {'gallery': current_gallery, 
                                         'brother_galleries': brother_galleries, 
                                         'search_options_form': SearchOptionsForm(),
                                         }, context_instance=RequestContext(request)
                              )


def photo(request, gallery_slugs, photo_slug):
    parent_slug, current_gallery = process_category_thread(request, gallery_slugs)
    parent_category = current_gallery.parent

    photo = Photo.objects.get(title_slug=photo_slug)    
    
    return render_to_response('website/photo.html', {
            'photo': photo, 
            'parent_category': parent_category,
            'gallery_slugs': gallery_slugs,
            'search_options_form': SearchOptionsForm(),
            }, context_instance=RequestContext(request))


def search_photos(request):
    query = request.GET.get("query", None)
    if request.method == 'GET' and query: 
        form = SearchOptionsForm(request.GET)
        photos = Photo.objects.search_filter(request.GET).order_by("title")
        no_image_thumb_url = os.path.join(settings.MEDIA_URL, settings.DAG_NO_IMAGE[settings.DAG_GALLERY_THUMB_SIZE_KEY])
        response = render_to_response(
            'website/search_results.html', {
                'photos': photos,
                'query': request.GET.get("query", None),
                'num_results': len(photos),
                'no_image_thumb_url': no_image_thumb_url,
                'search_options_form': SearchOptionsForm(),
                },
            context_instance=RequestContext(request))
    else:
        response = HttpResponseBadRequest()
    return response


def send_request_photos(request):
    if request.method == 'POST': 
        subject = "[Barres Fotonatura] Solicitud de fotografías"
        message = request.POST.get("message", "")
        sender_email = request.POST.get("email", "")
        photo_items = request.POST.getlist("shopping-cart-items[]")
        redirect_to_url = request.POST.get("redirect_to_url", "/")
        try:
            t = get_template('website/request_photos_mail.html')
            photos = Photo.objects.filter(pk__in=photo_items)
            no_image_thumb_url = os.path.join(settings.MEDIA_URL, settings.DAG_NO_IMAGE[settings.DAG_GALLERY_THUMB_SIZE_KEY])
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
        response = HttpResponseRedirect(redirect_to_url)
        response.delete_cookie(settings.DAGUERRO_CART_SESSION_KEY)
        return response
    else: 
        return HttpResponseBadRequest("Only POST method allowed.")
 

def _send_html_mail(msg):
    msg.attach_alternative(msg.body, "text/html")            
    msg.send()

