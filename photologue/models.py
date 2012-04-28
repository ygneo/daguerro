# -*- coding: utf-8 -*-
import os
import random
import shutil
import zipfile

from datetime import datetime
from inspect import isclass

from django.db import models
from django.db.models.signals import post_init
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils.functional import curry
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode
from django.core.paginator import Paginator
from django.db.models import Q

from south.modelsinspector import add_introspection_rules
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager

# Required PIL classes may or may not be available from the root namespace
# depending on the installation method used.
try:
    import Image
    import ImageFile
    import ImageFilter
    import ImageEnhance
except ImportError:
    try:
        from PIL import Image
        from PIL import ImageFile
        from PIL import ImageFilter
        from PIL import ImageEnhance
    except ImportError:
        raise ImportError('Photologue was unable to import the Python Imaging Library. Please confirm it`s installed and available on your current Python path.')

# load the django-tagging TagField from default location,
# otherwise we substitude a dummy TagField.
try:
    from tagging.fields import TagField
    tagfield_help_text = _('Separate tags with spaces, put quotes around multiple-word tags.')
except ImportError:
    class TagField(models.CharField):
        def __init__(self, **kwargs):
            default_kwargs = {'max_length': 255, 'blank': True}
            default_kwargs.update(kwargs)
            super(TagField, self).__init__(**default_kwargs)
        def get_internal_type(self):
            return 'CharField'
    # TODO: Move exising data to django tagging
    #tagfield_help_text = _('Django-tagging was not found, tags will be treated as plain text.')
    tagfield_help_text = _('Separate tags with spaces, put quotes around multiple-word tags.')

from utils import EXIF
from utils.reflection import add_reflection
from utils.watermark import apply_watermark

# Path to sample image
SAMPLE_IMAGE_PATH = getattr(settings, 'SAMPLE_IMAGE_PATH', os.path.join(os.path.dirname(__file__), 'res', 'sample.jpg')) # os.path.join(settings.PROJECT_PATH, 'photologue', 'res', 'sample.jpg'

# Modify image file buffer size.
ImageFile.MAXBLOCK = getattr(settings, 'PHOTOLOGUE_MAXBLOCK', 256 * 2 ** 10)

# Photologue image path relative to media root
PHOTOLOGUE_DIR = getattr(settings, 'PHOTOLOGUE_DIR', 'photologue')

# Look for user function to define file paths
PHOTOLOGUE_PATH = getattr(settings, 'PHOTOLOGUE_PATH', None)
if PHOTOLOGUE_PATH is not None:
    if callable(PHOTOLOGUE_PATH):
        get_storage_path = PHOTOLOGUE_PATH
    else:
        parts = PHOTOLOGUE_PATH.split('.')
        module_name = '.'.join(parts[:-1])
        module = __import__(module_name)
        get_storage_path = getattr(module, parts[-1])
else:
    def get_storage_path(instance, filename):
        return os.path.join(PHOTOLOGUE_DIR, 'photos', filename)

# Quality options for JPEG images
JPEG_QUALITY_CHOICES = (
    (30, _('Very Low')),
    (40, _('Low')),
    (50, _('Medium-Low')),
    (60, _('Medium')),
    (70, _('Medium-High')),
    (80, _('High')),
    (90, _('Very High')),
)

# choices for new crop_anchor field in Photo
CROP_ANCHOR_CHOICES = (
    ('top', _('Top')),
    ('right', _('Right')),
    ('bottom', _('Bottom')),
    ('left', _('Left')),
    ('center', _('Center (Default)')),
)

IMAGE_TRANSPOSE_CHOICES = (
    ('FLIP_LEFT_RIGHT', _('Flip left to right')),
    ('FLIP_TOP_BOTTOM', _('Flip top to bottom')),
    ('ROTATE_90', _('Rotate 90 degrees counter-clockwise')),
    ('ROTATE_270', _('Rotate 90 degrees clockwise')),
    ('ROTATE_180', _('Rotate 180 degrees')),
)

WATERMARK_STYLE_CHOICES = (
    ('tile', _('Tile')),
    ('scale', _('Scale')),
)

# Prepare a list of image filters
filter_names = []
for n in dir(ImageFilter):
    klass = getattr(ImageFilter, n)
    if isclass(klass) and issubclass(klass, ImageFilter.BuiltinFilter) and \
        hasattr(klass, 'name'):
            filter_names.append(klass.__name__)
IMAGE_FILTERS_HELP_TEXT = _('Chain multiple filters using the following pattern "FILTER_ONE->FILTER_TWO->FILTER_THREE". Image filters will be applied in order. The following filters are available: %s.' % (', '.join(filter_names)))

class Gallery(MPTTModel):
    date_added = models.DateTimeField(_('Creation date'), default=datetime.now)
    title = models.CharField(_('Title'), max_length=100, unique=True)
    title_slug = models.SlugField(_('Slug'), unique=True,
                                  help_text=_('A "slug" is a unique URL-friendly title for an object.'))
    parent = TreeForeignKey('self', verbose_name=_("Parent category"), blank=True, null=True, related_name='children')
    order = models.IntegerField(verbose_name=_("Order"), blank=True, null=True)
    description = models.TextField(_('Description'), blank=True)
    photo = models.ForeignKey('Photo', verbose_name=_("Photo"), blank=True, null=True, related_name="gallery_photo")
    is_public = models.BooleanField(_('is public'), default=True, help_text=_('Public galleries will be displayed in the default views.'))
    photos = models.ManyToManyField('Photo', related_name='galleries', verbose_name=_('photos'),
                                    null=True, blank=True)
    tags = TagField(help_text=tagfield_help_text, verbose_name=_('tags'))

    class Meta:
        ordering = ['order']
        get_latest_by = 'date_added'
        verbose_name = _('categoria')
        verbose_name_plural = _('categorias')

    class MPTTMeta:
        order_insertion_by = ['order']
        parent_attr = 'parent'

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.__unicode__()

    def get_absolute_url(self):
        return reverse('pl-gallery', args=[self.title_slug])

    def latest(self, limit=0, public=True):
        if limit == 0:
            limit = self.photo_count()
        if public:
            return self.public()[:limit]
        else:
            return self.photos.all()[:limit]

    def sample(self, count=0, public=True):
        if count == 0 or count > self.photo_count():
            count = self.photo_count()
        if public:
            photo_set = self.public()
        else:
            photo_set = self.photos.all()
        return random.sample(photo_set, count)

    def photo_count(self, public=True):
        if public:
            return self.public().count()
        else:
            return self.photos.all().count()
    photo_count.short_description = _('count')

    def slugs_path(self):
        parent = self.parent
        slugs = ''
        while parent is not None:
            slugs = parent.title_slug + "/" + slugs
            parent = parent.parent
        return slugs + self.title_slug

    def get_parents(self):
        parent = self.parent
        parents = []
        while parent is not None:
            parents.append(parent.title)
            parent = parent.parent
        return parents
        

class GalleryUpload(models.Model):
    zip_file = models.FileField(_('images file (.zip)'), upload_to=PHOTOLOGUE_DIR+"/temp",
                                help_text=_('Select a .zip file of images to upload into a new Gallery.'))
    gallery = models.ForeignKey(Gallery, null=True, blank=True, help_text=_('Select a gallery to add these images to. leave this empty to create a new gallery from the supplied title.'))
    title = models.CharField(_('title'), max_length=75, help_text=_('All photos in the gallery will be given a title made up of the gallery title + a sequential number.'))
    caption = models.TextField(_('caption'), blank=True, help_text=_('Caption will be added to all photos.'))
    description = models.TextField(_('description'), blank=True, help_text=_('A description of this Gallery.'))
    is_public = models.BooleanField(_('is public'), default=True, help_text=_('Uncheck this to make the uploaded gallery and included photographs private.'))
    tags = models.CharField(max_length=255, blank=True, help_text=tagfield_help_text, verbose_name=_('tags'))

    class Meta:
        verbose_name = _('gallery upload')
        verbose_name_plural = _('gallery uploads')

    def save(self, *args, **kwargs):
        super(GalleryUpload, self).save(*args, **kwargs)
        gallery = self.process_zipfile()
        super(GalleryUpload, self).delete()
        return gallery

    def process_zipfile(self):
        if os.path.isfile(self.zip_file.path):
            # TODO: implement try-except here
            zip = zipfile.ZipFile(self.zip_file.path)
            bad_file = zip.testzip()
            if bad_file:
                raise Exception('"%s" in the .zip archive is corrupt.' % bad_file)
            count = 1
            if self.gallery:
                gallery = self.gallery
            else:
                gallery = Gallery.objects.create(title=self.title,
                                                 title_slug=slugify(self.title),
                                                 description=self.description,
                                                 is_public=self.is_public,
                                                 tags=self.tags)
            from cStringIO import StringIO
            for filename in zip.namelist():
                if filename.startswith('__'): # do not process meta files
                    continue
                data = zip.read(filename)
                if len(data):
                    try:
                        # the following is taken from django.newforms.fields.ImageField:
                        #  load() is the only method that can spot a truncated JPEG,
                        #  but it cannot be called sanely after verify()
                        trial_image = Image.open(StringIO(data))
                        trial_image.load()
                        # verify() is the only method that can spot a corrupt PNG,
                        #  but it must be called immediately after the constructor
                        trial_image = Image.open(StringIO(data))
                        trial_image.verify()
                    except Exception:
                        # if a "bad" file is found we just skip it.
                        continue
                    while 1:
                        title = ' '.join([self.title, str(count)])
                        slug = slugify(title)
                        try:
                            p = Photo.objects.get(title_slug=slug)
                        except Photo.DoesNotExist:
                            photo = Photo(title=title,
                                          title_slug=slug,
                                          caption=self.caption,
                                          is_public=self.is_public,
                                          tags=self.tags)
                            photo.image.save(filename, ContentFile(data))
                            gallery.photos.add(photo)
                            count = count + 1
                            break
                        count = count + 1
            zip.close()
            return gallery


class ImageModel(models.Model):
    image = models.ImageField(_('image'), upload_to=get_storage_path, blank=False)
    date_taken = models.DateTimeField(_('date taken'), null=True, blank=True, editable=False)
    view_count = models.PositiveIntegerField(default=0, editable=False)
    crop_from = models.CharField(_('crop from'), blank=True, max_length=10, default='center', choices=CROP_ANCHOR_CHOICES)
    effect = models.ForeignKey('PhotoEffect', null=True, blank=True, related_name="%(class)s_related", verbose_name=_('effect'))

    class Meta:
        abstract = True

    @property
    def EXIF(self):
        try:
            return EXIF.process_file(open(self.image.path, 'rb'))
        except:
            try:
                return EXIF.process_file(open(self.image.path, 'rb'), details=False)
            except:
                return {}

    def admin_thumbnail(self):
        func = getattr(self, 'get_admin_thumbnail_url', None)
        if func is None:
            return _('An "admin_thumbnail" photo size has not been defined.')
        else:
            if hasattr(self, 'get_absolute_url'):
                return u'<a href="%s"><img src="%s"></a>' % \
                    (self.get_absolute_url(), func())
            else:
                return u'<a href="%s"><img src="%s"></a>' % \
                    (self.image.url, func())
    admin_thumbnail.short_description = _('Thumbnail')
    admin_thumbnail.allow_tags = True

    def cache_path(self):
        return os.path.join(os.path.dirname(self.image.path), "cache")

    def cache_url(self):
        return '/'.join([os.path.dirname(self.image.url), "cache"])

    def image_filename(self):
        return os.path.basename(self.image.path)

    def get_original_url(self):
        return "%s%s/photos/%s" % (settings.MEDIA_URL, PHOTOLOGUE_DIR, self.image_filename())

    def _get_filename_for_size(self, size):
        size = getattr(size, 'name', size)
        base, ext = os.path.splitext(self.image_filename())
        return ''.join([smart_unicode(base), '_', size, ext])

    def _get_SIZE_photosize(self, size):
        return PhotoSizeCache().sizes.get(size)

    def _get_SIZE_size(self, size):
        photosize = PhotoSizeCache().sizes.get(size)
        if not self.size_exists(photosize):
            self.create_size(photosize)
        return Image.open(self._get_SIZE_filename(size)).size

    def _get_SIZE_url(self, size):
        photosize = PhotoSizeCache().sizes.get(size)
        if not self.size_exists(photosize):
            self.create_size(photosize)
        if photosize.increment_count:
            self.increment_count()
        return '/'.join([self.cache_url(), self._get_filename_for_size(photosize.name)])

    def _get_SIZE_filename(self, size):
        photosize = PhotoSizeCache().sizes.get(size)
        return os.path.join(self.cache_path(),
                            self._get_filename_for_size(photosize.name))

    def increment_count(self):
        self.view_count += 1
        models.Model.save(self)

    def add_accessor_methods(self, *args, **kwargs):
        for size in PhotoSizeCache().sizes.keys():
            setattr(self, 'get_%s_size' % size,
                    curry(self._get_SIZE_size, size=size))
            setattr(self, 'get_%s_photosize' % size,
                    curry(self._get_SIZE_photosize, size=size))
            setattr(self, 'get_%s_url' % size,
                    curry(self._get_SIZE_url, size=size))
            setattr(self, 'get_%s_filename' % size,
                    curry(self._get_SIZE_filename, size=size))

    def size_exists(self, photosize):
        func = getattr(self, "get_%s_filename" % photosize.name, None)
        if func is not None:
            if os.path.isfile(func()):
                return True
        return False

    def resize_image(self, im, photosize):
        cur_width, cur_height = im.size
        new_width, new_height = photosize.size
        if photosize.crop:
            ratio = max(float(new_width)/cur_width,float(new_height)/cur_height)
            x = (cur_width * ratio)
            y = (cur_height * ratio)
            xd = abs(new_width - x)
            yd = abs(new_height - y)
            x_diff = int(xd / 2)
            y_diff = int(yd / 2)
            if self.crop_from == 'top':
                box = (int(x_diff), 0, int(x_diff+new_width), new_height)
            elif self.crop_from == 'left':
                box = (0, int(y_diff), new_width, int(y_diff+new_height))
            elif self.crop_from == 'bottom':
                box = (int(x_diff), int(yd), int(x_diff+new_width), int(y)) # y - yd = new_height
            elif self.crop_from == 'right':
                box = (int(xd), int(y_diff), int(x), int(y_diff+new_height)) # x - xd = new_width
            else:
                box = (int(x_diff), int(y_diff), int(x_diff+new_width), int(y_diff+new_height))
            im = im.resize((int(x), int(y)), Image.ANTIALIAS).crop(box)
        else:
            if not new_width == 0 and not new_height == 0:
                ratio = min(float(new_width)/cur_width,
                            float(new_height)/cur_height)
            else:
                if new_width == 0:
                    ratio = float(new_height)/cur_height
                else:
                    ratio = float(new_width)/cur_width
            new_dimensions = (int(round(cur_width*ratio)),
                              int(round(cur_height*ratio)))
            if new_dimensions[0] > cur_width or \
               new_dimensions[1] > cur_height:
                if not photosize.upscale:
                    return im
            im = im.resize(new_dimensions, Image.ANTIALIAS)
        return im

    def create_size(self, photosize):
        if self.size_exists(photosize):
            return
        if not os.path.isdir(self.cache_path()):
            os.makedirs(self.cache_path())
        try:
            im = Image.open(self.image.path)
        except IOError:
            return
        # Save the original format
        im_format = im.format
        # Apply effect if found
        if self.effect is not None:
            im = self.effect.pre_process(im)
        elif photosize.effect is not None:
            im = photosize.effect.pre_process(im)
        # Resize/crop image
        if im.size != photosize.size and photosize.size != (0, 0):
            im = self.resize_image(im, photosize)
        # Apply watermark if found
        if photosize.watermark is not None:
            im = photosize.watermark.post_process(im)
        # Apply effect if found
        if self.effect is not None:
            im = self.effect.post_process(im)
        elif photosize.effect is not None:
            im = photosize.effect.post_process(im)
        # Save file
        im_filename = getattr(self, "get_%s_filename" % photosize.name)()
        try:
            if im_format != 'JPEG':
                try:
                    im.save(im_filename)
                    return
                except KeyError:
                    pass
            dpi = im.info['dpi'] if 'dpi' in im.info else (300, 300)
            im.save(im_filename, 'JPEG', quality=int(photosize.quality), dpi=dpi, optimize=True)
        except IOError, e:
            if os.path.isfile(im_filename):
                os.unlink(im_filename)
            raise e

    def remove_size(self, photosize, remove_dirs=True):
        if not self.size_exists(photosize):
            return
        filename = getattr(self, "get_%s_filename" % photosize.name)()
        if os.path.isfile(filename):
            os.remove(filename)
        if remove_dirs:
            self.remove_cache_dirs()

    def clear_cache(self):
        cache = PhotoSizeCache()
        for photosize in cache.sizes.values():
            self.remove_size(photosize, False)
        self.remove_cache_dirs()

    def pre_cache(self):
        cache = PhotoSizeCache()
        for photosize in cache.sizes.values():
            if photosize.pre_cache:
                self.create_size(photosize)

    def remove_cache_dirs(self):
        try:
            os.removedirs(self.cache_path())
        except:
            pass

    def save(self, *args, **kwargs):
        if self.date_taken is None:
            try:
                exif_date = self.EXIF.get('EXIF DateTimeOriginal', None)
                if exif_date is not None:
                    d, t = str.split(exif_date.values)
                    year, month, day = d.split(':')
                    hour, minute, second = t.split(':')
                    self.date_taken = datetime(int(year), int(month), int(day),
                                               int(hour), int(minute), int(second))
            except:
                pass
        if self.date_taken is None:
            self.date_taken = datetime.now()
        if self._get_pk_val():
            self.clear_cache()
        super(ImageModel, self).save(*args, **kwargs)
        self.pre_cache()

    def delete(self):
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (self._meta.object_name, self._meta.pk.attname)
        self.clear_cache()
        super(ImageModel, self).delete()

class PhotoManager(models.Manager):
    
    def public(self):
        return self.filter(is_public=True)

    def search_filter(self, query_string):
        queryset = self.get_query_set()
        queryset = queryset.filter(~Q(galleries=None), is_public=True)
        query_filters = []
        for key, value in query_string.iteritems():
            if value == 'on':
                if search_mode == "TOTAL":
                    pattern = self.build_pattern(query)
                    query_filters.append(Q(**{'%s__iregex' % key: pattern}))
                else:
                    query_filters.append(Q(**{'%s__icontains' % key: query}))

        query_filter = query_filters.pop()
        for qfilter in query_filters:
            query_filter |= qfilter

        if search_galleries == 'SELECTED':
            gallery_ids = query_string['gallery_ids'].split(",")
            queryset = queryset.filter(galleries__in=gallery_ids)

        return queryset.filter(query_filter)

    def build_pattern(self, query):
        accented_vowel = {'a': u'á', 'e': u'é', 'i': u'í', 'o': u'ó', 'u': u'ú', 
                          'A': u'À', 'E': u'É', 'I': u'Í', 'O': u'Ó', 'U': u'Ú'}
        pattern = ""
        for char in query:
            if char in set('aeiouAEIOU'):
                char = u"[%s%s]" % (char, accented_vowel[char])
            pattern += char
        return r"[[:<:]]%s[[:>:]]" % pattern

        


add_introspection_rules([], ["^photologue\.models\.TagField"])
class Photo(ImageModel):
    title = models.CharField(_('Title'), max_length=100, unique=True)
    title_slug = models.SlugField(_('Slug'), unique=True,
                                  help_text=('A "slug" is a unique URL-friendly title for an object.'))
    alternative_title = models.CharField(_('Alternative title'), max_length=200, blank=True, null=True)
    alternative_title_url = models.URLField(_('Alternative title URL'), blank=True, null=True,)
    caption = models.TextField(blank=True)
    date_added = models.DateTimeField(_('Date added'), default=datetime.now, editable=False)
    order = models.IntegerField(_('Order'), blank=True, null=True)
    is_public = models.BooleanField(_('Public'), default=True, 
                                    help_text=_('Public photographs will be displayed in the default views.'))
    tags = TagField(help_text=tagfield_help_text, verbose_name=_('Tags'))
    location_title = models.CharField(_('Location'), max_length=300, blank=True, null=True,)
    family = models.CharField(_('Family'), max_length=200, blank=True, null=True)
    latitude = models.FloatField(_('Latitude'), blank=True, null=True)
    longitude = models.FloatField(_('Longitude'), blank=True, null=True)
#    gallery = models.ForeignKey(Gallery, related_name="photos", null=True)
    objects = PhotoManager()

    class Meta:
        ordering = ['order', 'title']
        get_latest_by = 'date_added'
        verbose_name = _("photo")
        verbose_name_plural = _("photos")

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.__unicode__()

    def save(self, *args, **kwargs):
        self.title_slug = slugify(self.title)
        super(Photo, self).save(*args, **kwargs)

    def public_galleries(self):
        """Return the public galleries to which this photo belongs."""
        return self.galleries.filter(is_public=True)

    def get_absolute_url(self):
        return reverse('pl-photo', args=[self.title_slug])

    def get_daguerro_url(self):
        galleries = self.galleries.all()
        if galleries:
            slugs_path = galleries[0].slugs_path() 
        else:
            slugs_path = ''
        return reverse('daguerro-gallery-photo', args=[slugs_path, self.title_slug])

    def get_website_url(self):
        try:
            slugs = self.galleries.all()[0].slugs_path()
        except IndexError:
            slugs = ''
        return slugs + "/foto/" + self.title_slug

    def get_previous_in_gallery(self, gallery):
        try:
            return self.get_previous_by_date_added(galleries__exact=gallery,
                                                   is_public=True)
        except Photo.DoesNotExist:
            return None

    def get_next_in_gallery(self, gallery):
        try:
            return self.get_next_by_date_added(galleries__exact=gallery,
                                               is_public=True)
        except Photo.DoesNotExist:
            return None

    def get_avaliable_title(self):
        avaliable_title = self.title
        num_photos = Photo.objects.filter(title=self.title).count()
        if num_photos:
            avaliable_title = "%s-%s" % (self.title, num_photos)
        return avaliable_title
        
    def delete(self):
        """Override delete method so related gallery using a photo as its representation image is not deleted"""
        self.gallery_set.clear()
        super(Photo, self).delete()
        


class BaseEffect(models.Model):
    name = models.CharField(_('name'), max_length=30, unique=True)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        abstract = True

    def sample_dir(self):
        return os.path.join(settings.MEDIA_ROOT, PHOTOLOGUE_DIR, 'samples')

    def sample_url(self):
        return settings.MEDIA_URL + '/'.join([PHOTOLOGUE_DIR, 'samples', '%s %s.jpg' % (self.name.lower(), 'sample')])

    def sample_filename(self):
        return os.path.join(self.sample_dir(), '%s %s.jpg' % (self.name.lower(), 'sample'))

    def create_sample(self):
        if not os.path.isdir(self.sample_dir()):
            os.makedirs(self.sample_dir())
        try:
            im = Image.open(SAMPLE_IMAGE_PATH)
        except IOError:
            raise IOError('Photologue was unable to open the sample image: %s.' % SAMPLE_IMAGE_PATH)
        im = self.process(im)
        im.save(self.sample_filename(), 'JPEG', quality=90, optimize=True)

    def admin_sample(self):
        return u'<img src="%s">' % self.sample_url()
    admin_sample.short_description = 'Sample'
    admin_sample.allow_tags = True

    def pre_process(self, im):
        return im

    def post_process(self, im):
        return im

    def process(self, im):
        im = self.pre_process(im)
        im = self.post_process(im)
        return im

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    def save(self, *args, **kwargs):
        try:
            os.remove(self.sample_filename())
        except:
            pass
        models.Model.save(self, *args, **kwargs)
        self.create_sample()
        for size in self.photo_sizes.all():
            size.clear_cache()
        # try to clear all related subclasses of ImageModel
        for prop in [prop for prop in dir(self) if prop[-8:] == '_related']:
            for obj in getattr(self, prop).all():
                obj.clear_cache()
                obj.pre_cache()

    def delete(self):
        try:
            os.remove(self.sample_filename())
        except:
            pass
        models.Model.delete(self)


class PhotoEffect(BaseEffect):
    """ A pre-defined effect to apply to photos """
    transpose_method = models.CharField(_('rotate or flip'), max_length=15, blank=True, choices=IMAGE_TRANSPOSE_CHOICES)
    color = models.FloatField(_('color'), default=1.0, help_text=_("A factor of 0.0 gives a black and white image, a factor of 1.0 gives the original image."))
    brightness = models.FloatField(_('brightness'), default=1.0, help_text=_("A factor of 0.0 gives a black image, a factor of 1.0 gives the original image."))
    contrast = models.FloatField(_('contrast'), default=1.0, help_text=_("A factor of 0.0 gives a solid grey image, a factor of 1.0 gives the original image."))
    sharpness = models.FloatField(_('sharpness'), default=1.0, help_text=_("A factor of 0.0 gives a blurred image, a factor of 1.0 gives the original image."))
    filters = models.CharField(_('filters'), max_length=200, blank=True, help_text=_(IMAGE_FILTERS_HELP_TEXT))
    reflection_size = models.FloatField(_('size'), default=0, help_text=_("The height of the reflection as a percentage of the orignal image. A factor of 0.0 adds no reflection, a factor of 1.0 adds a reflection equal to the height of the orignal image."))
    reflection_strength = models.FloatField(_('strength'), default=0.6, help_text=_("The initial opacity of the reflection gradient."))
    background_color = models.CharField(_('color'), max_length=7, default="#FFFFFF", help_text=_("The background color of the reflection gradient. Set this to match the background color of your page."))

    class Meta:
        verbose_name = _("photo effect")
        verbose_name_plural = _("photo effects")

    def pre_process(self, im):
        if self.transpose_method != '':
            method = getattr(Image, self.transpose_method)
            im = im.transpose(method)
        if im.mode != 'RGB' and im.mode != 'RGBA':
            return im
        for name in ['Color', 'Brightness', 'Contrast', 'Sharpness']:
            factor = getattr(self, name.lower())
            if factor != 1.0:
                im = getattr(ImageEnhance, name)(im).enhance(factor)
        for name in self.filters.split('->'):
            image_filter = getattr(ImageFilter, name.upper(), None)
            if image_filter is not None:
                try:
                    im = im.filter(image_filter)
                except ValueError:
                    pass
        return im

    def post_process(self, im):
        if self.reflection_size != 0.0:
            im = add_reflection(im, bgcolor=self.background_color, amount=self.reflection_size, opacity=self.reflection_strength)
        return im


class Watermark(BaseEffect):
    image = models.ImageField(_('image'), upload_to=PHOTOLOGUE_DIR+"/watermarks")
    style = models.CharField(_('style'), max_length=5, choices=WATERMARK_STYLE_CHOICES, default='scale')
    opacity = models.FloatField(_('opacity'), default=1, help_text=_("The opacity of the overlay."))

    class Meta:
        verbose_name = _('watermark')
        verbose_name_plural = _('watermarks')

    def post_process(self, im):
        mark = Image.open(self.image.path)
        return apply_watermark(im, mark, self.style, self.opacity)


class PhotoSize(models.Model):
    name = models.CharField(_('name'), max_length=20, unique=True, help_text=_('Photo size name should contain only letters, numbers and underscores. Examples: "thumbnail", "display", "small", "main_page_widget".'))
    width = models.PositiveIntegerField(_('width'), default=0, help_text=_('If width is set to "0" the image will be scaled to the supplied height.'))
    height = models.PositiveIntegerField(_('height'), default=0, help_text=_('If height is set to "0" the image will be scaled to the supplied width'))
    quality = models.PositiveIntegerField(_('quality'), choices=JPEG_QUALITY_CHOICES, default=70, help_text=_('JPEG image quality.'))
    upscale = models.BooleanField(_('upscale images?'), default=False, help_text=_('If selected the image will be scaled up if necessary to fit the supplied dimensions. Cropped sizes will be upscaled regardless of this setting.'))
    crop = models.BooleanField(_('crop to fit?'), default=False, help_text=_('If selected the image will be scaled and cropped to fit the supplied dimensions.'))
    pre_cache = models.BooleanField(_('pre-cache?'), default=False, help_text=_('If selected this photo size will be pre-cached as photos are added.'))
    increment_count = models.BooleanField(_('increment view count?'), default=False, help_text=_('If selected the image\'s "view_count" will be incremented when this photo size is displayed.'))
    effect = models.ForeignKey('PhotoEffect', null=True, blank=True, related_name='photo_sizes', verbose_name=_('photo effect'))
    watermark = models.ForeignKey('Watermark', null=True, blank=True, related_name='photo_sizes', verbose_name=_('watermark image'))

    class Meta:
        ordering = ['width', 'height']
        verbose_name = _('photo size')
        verbose_name_plural = _('photo sizes')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    def clear_cache(self):
        for cls in ImageModel.__subclasses__():
            for obj in cls.objects.all():
                obj.remove_size(self)
                if self.pre_cache:
                    obj.create_size(self)
        PhotoSizeCache().reset()

    def save(self, *args, **kwargs):
        if self.crop is True:
            if self.width == 0 or self.height == 0:
                raise ValueError("PhotoSize width and/or height can not be zero if crop=True.")
        super(PhotoSize, self).save(*args, **kwargs)
        PhotoSizeCache().reset()
        self.clear_cache()

    def delete(self):
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (self._meta.object_name, self._meta.pk.attname)
        self.clear_cache()
        super(PhotoSize, self).delete()

    def _get_size(self):
        return (self.width, self.height)
    def _set_size(self, value):
        self.width, self.height = value
    size = property(_get_size, _set_size)


class PhotoSizeCache(object):
    __state = {"sizes": {}}

    def __init__(self):
        self.__dict__ = self.__state
        if not len(self.sizes):
            sizes = PhotoSize.objects.all()
            for size in sizes:
                self.sizes[size.name] = size

    def reset(self):
        self.sizes = {}


# Set up the accessor methods
def add_methods(sender, instance, signal, *args, **kwargs):
    """ Adds methods to access sized images (urls, paths)

    after the Photo model's __init__ function completes,
    this method calls "add_accessor_methods" on each instance.
    """
    if hasattr(instance, 'add_accessor_methods'):
        instance.add_accessor_methods()

# connect the add_accessor_methods function to the post_init signal
post_init.connect(add_methods)


