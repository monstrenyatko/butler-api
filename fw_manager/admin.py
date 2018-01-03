from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from . import models as local_models


class FirmwareModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'hardware', 'description', 'upload_date', 'get_file_link',)
    ordering = ('name',)
    search_fields = ('name', 'description',)
    list_filter = ('hardware',)

    def get_file_link(self, obj):
        return mark_safe('<a href="{}" download="{}">{}</a>'.format(
            obj.file.url,
            'fw_{}.bin'.format(obj.name),
            'download',
        ))
    get_file_link.short_description = 'file'


class FirmwareAssignmentModelAdmin(admin.ModelAdmin):
    list_select_related = ('user', 'value',)
    list_display = ('user', 'get_firmware_link', 'get_hardware',)
    list_filter = ('value__hardware',)
    ordering = ('user__username',)
    search_fields = ('user__username', 'value__name', 'value__hardware',)
    fields = ('value',)
    readonly_fields = ()

    def get_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ('get_user_link',) + self.fields
        return ('user',) + self.fields

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ('get_user_link',) + self.readonly_fields
        return self.readonly_fields

    def get_user_link(self, obj):
        url = reverse('admin:{}_{}_change'.format(
                obj.user._meta.app_label,
                obj.user._meta.model_name
            ),
            args=[obj.user.pk]
        )
        return mark_safe('<a href="{}">{}</a>'.format(
            url, obj.user.username
        ))
    get_user_link.short_description = 'user'

    def get_firmware_link(self, obj):
        url = reverse('admin:{}_{}_change'.format(
                obj.value._meta.app_label,
                obj.value._meta.model_name
            ),
            args=[obj.value.pk]
        )
        return mark_safe('<a href="{}">{}</a>'.format(
            url, obj.value.name
        ))
    get_firmware_link.short_description = 'firmware'

    def get_hardware(self, obj):
        return obj.value.hardware
    get_hardware.short_description = 'hardware'


admin.site.register(local_models.FirmwareModel, FirmwareModelAdmin)
admin.site.register(local_models.FirmwareAssignmentModel, FirmwareAssignmentModelAdmin)
