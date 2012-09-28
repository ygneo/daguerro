from django.contrib import admin
from models import CustomField, GenericCustomField


class CustomFieldAdmin(admin.ModelAdmin):
    readonly_fields = ("name",)


admin.site.register(CustomField, CustomFieldAdmin)
admin.site.register(GenericCustomField)
