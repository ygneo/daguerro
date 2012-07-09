""" Newforms Admin configuration for Photologue

"""
from django.contrib import admin
from models import *
from mptt.admin import MPTTModelAdmin

class GalleryAdmin(MPTTModelAdmin):
    exclude = ('order', 'date_added',)
    list_display = ('title', 'is_public')
    list_filter = ['is_public']
    prepopulated_fields = {'title_slug': ('title',)}
    filter_horizontal = ('photos',)

class PhotoAdmin(admin.ModelAdmin):
    exclude = ('crop_from', 'effect', 'order', )
    list_display = ('title',  'is_public',  'admin_thumbnail')
    list_filter = ['is_public']
    search_fields = ['title', 'caption']
    list_per_page = 10
    prepopulated_fields = {'title_slug': ('title',)}

class PhotoEffectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'color', 'brightness', 'contrast', 'sharpness', 'filters', 'admin_sample')
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Adjustments', {
            'fields': ('color', 'brightness', 'contrast', 'sharpness')
        }),
        ('Filters', {
            'fields': ('filters',)
        }),
        ('Reflection', {
            'fields': ('reflection_size', 'reflection_strength', 'background_color')
        }),
        ('Transpose', {
            'fields': ('transpose_method',)
        }),
    )

class PhotoSizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'width', 'height', 'crop', 'pre_cache', 'effect', 'increment_count')
    fieldsets = (
        (None, {
            'fields': ('name', 'width', 'height', 'quality')
        }),
        ('Options', {
            'fields': ('upscale', 'crop', 'pre_cache', 'increment_count')
        }),
        ('Enhancements', {
            'fields': ('effect', 'watermark',)
        }),
    )

class WatermarkAdmin(admin.ModelAdmin):
    list_display = ('name', 'opacity', 'style')


admin.site.register(Gallery, GalleryAdmin)
admin.site.register(GalleryUpload)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(PhotoEffect, PhotoEffectAdmin)
admin.site.register(PhotoSize, PhotoSizeAdmin)
admin.site.register(Watermark, WatermarkAdmin)
