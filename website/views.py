#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, QueryDict
from django.core.mail import send_mail, BadHeaderError
from django.template import Context, Template
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives, EmailMessage
from photologue.models import Gallery, Photo
from haystack.views import SearchView
from daguerro.utils import process_category_thread
from daguerro.paginator import DiggPaginator
from website.forms import ShoppingCartForm, SearchOptionsForm


def gallery(request, slugs=None):
    parent_slug, current_gallery = process_category_thread(request, slugs)
    no_image_thumb_url = os.path.join(settings.STATIC_URL, 
                                          settings.DAG_NO_IMAGE[settings.DAG_GALLERY_THUMB_SIZE_KEY])
    
    # TODO Find a better way to do this (parent by default for a category, i.e. root)
    if current_gallery:
        children_galleries = current_gallery.get_children().filter(is_public=True)
        brother_galleries = current_gallery.get_siblings(include_self=True).filter(is_public=True)
        photos = current_gallery.photos.public()
    else:
        brother_galleries = None
        children_galleries = None
        photos = []

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

    photo = Photo.objects.get(title_slug=photo_slug)    
    
    return render_to_response('website/photo.html', {
            'photo': photo, 
            'parent_category': parent_category,
            'gallery_slugs': gallery_slugs,
            'search_options_form': SearchOptionsForm(),
            }, context_instance=RequestContext(request))


class SearchPhotosView(SearchView):
    template = 'website/search_results.html'

    def __init__(self, *args, **kwargs):
        kwargs['form_class'] = SearchOptionsForm
        super(SearchPhotosView, self).__init__(*args, **kwargs)

    
    def build_page(self):
        """
        Paginates the results appropriately.

        In case someone does not want to use Django's built-in pagination, it
        should be a simple matter to override this method to do what they would
        like.
        """
        try:
            page_no = int(self.request.GET.get('page', 1))
        except (TypeError, ValueError):
            raise Http404("Not a valid number for page.")

        if page_no < 1:
            raise Http404("Pages should be 1 or greater.")

        start_offset = (page_no - 1) * self.results_per_page
        self.results[start_offset:start_offset + self.results_per_page]

        paginator = DiggPaginator(self.results, self.results_per_page)

        try:
            page = paginator.page(page_no)
        except InvalidPage:
            raise Http404("No such page!")

        return (paginator, page)

    
    def extra_context(self):
        getvars = QueryDict(self.request.GET.urlencode(), mutable=True)
        try:
            getvars.pop("page")
        except KeyError:
            pass
        getvars = getvars.urlencode()

        show_galleries_tree = False
        if self.form.is_valid():
            if self.form.cleaned_data.get('search_galleries_choice', None) == "SELECTED":
                show_galleries_tree = True

        no_image_thumb_url = os.path.join(settings.STATIC_URL, 
                                          settings.DAG_NO_IMAGE[settings.DAG_GALLERY_THUMB_SIZE_KEY])

        return {'no_image_thumb_url': no_image_thumb_url,
                'search_options_form': self.form,
                'show_galleries_tree': show_galleries_tree,
                'getvars': getvars,
                }


def whoosh_search_index(request):
     from whoosh.index import open_dir
     from whoosh.query import Every
     from whoosh.qparser import QueryParser
     from django.utils.html import escape
     
     query = request.GET.get("q")
     
     ix = open_dir(settings.HAYSTACK_CONNECTIONS['default']['PATH'])
     qp = QueryParser("text", schema=ix.schema)
     if query:
         q = qp.parse(query)
     else:
         q = Every("text")
     results = ix.searcher().search(q)
     output = "<ul>"
     for result in results:
         output += "<li>" + escape(str(result)) + "</li>"
     output += "</ul>"
     return HttpResponse(output)
                        

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

