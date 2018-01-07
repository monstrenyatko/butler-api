from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.safestring import mark_safe
from rest_framework.authtoken.models import Token
from . import models as local_models


class RegionModelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)
    readonly_fields = ()

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ('name',) + self.readonly_fields
        return self.readonly_fields


class UserLocationModelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)
    readonly_fields = ()

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ('name',) + self.readonly_fields
        return self.readonly_fields


class UserProfileModelAdminInline(admin.StackedInline):
    model = local_models.UserProfileModel
    can_delete = False
    verbose_name_plural = 'profile'
    fk_name = 'user'


class UserProfileModelAdmin(admin.ModelAdmin):
    list_select_related = ('user',)
    list_display = ('user', 'is_device', 'is_auth_retrieved',)
    ordering = ('user__username',)
    search_fields = ('user__username',)
    list_filter = ('is_device',)
    fields = ('get_user_link', 'is_device', 'is_auth_retrieved', 'location', 'region',)
    readonly_fields = ('get_user_link',)

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

    def has_add_permission(self, request):
        return False


class UserModelAdmin(DjangoUserAdmin):
    list_select_related = ('profile',)
    list_display = DjangoUserAdmin.list_display + ('get_is_device', 'get_profile_link', 'get_auth_token_link',)
    list_filter = DjangoUserAdmin.list_filter + ('profile__is_device',)
    readonly_fields = ('get_profile_link',)
    inlines = (UserProfileModelAdminInline,)

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ('username',) + self.readonly_fields
        return self.readonly_fields

    def get_is_device(self, obj):
        return obj.profile.is_device
    get_is_device.short_description = 'is device'

    def get_profile_link(self, obj):
        url = reverse('admin:{}_{}_change'.format(
                obj.profile._meta.app_label,
                obj.profile._meta.model_name
            ),
            args=[obj.profile.pk]
        )
        return mark_safe('<a href="{}">{}</a>'.format(
            url, 'profile'
        ))
    get_profile_link.short_description = 'profile'

    def get_auth_token_link(self, obj):
        url = reverse('admin:{}_{}_change'.format(
                obj.auth_token._meta.app_label,
                obj.auth_token._meta.model_name
            ),
            args=[obj.auth_token.pk]
        )
        return mark_safe('<a href="{}">{}</a>'.format(
            url, 'token'
        ))
    get_auth_token_link.short_description = 'auth token'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserModelAdmin, self).get_inline_instances(request, obj)


class TokenModelAdmin(admin.ModelAdmin):
    list_select_related = ('user',)
    list_display = ('key', 'get_user_link', 'created',)
    ordering = ('user__username',)
    search_fields = ('user__username', 'key')
    fields = ('key', 'get_user_link', 'created',)
    readonly_fields = ('key', 'get_user_link', 'created',)

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

    def has_add_permission(self, request):
        return False


class MqttAclTemplateModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'template')
    readonly_fields = list_display

    def has_add_permission(self, request):
        return False


class MqttAclModelAdmin(admin.ModelAdmin):
    list_select_related = ('user',)
    list_display = ('get_user_link', 'get_topic_link', 'access',)
    list_filter = ('access',)
    ordering = ('user__username',)
    search_fields = ('user__username', 'topic')
    fields = ('topic', 'access',)
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

    def get_topic_link(self, obj):
        url = reverse('admin:{}_{}_change'.format(
                obj._meta.app_label,
                obj._meta.model_name
            ),
            args=[obj.pk]
        )
        return mark_safe('<a href="{}">{}</a>'.format(
            url, obj.topic
        ))
    get_topic_link.short_description = 'topic'


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserModelAdmin)

admin.site.register(local_models.RegionModel, RegionModelAdmin)

admin.site.register(local_models.UserLocationModel, UserLocationModelAdmin)

admin.site.register(local_models.UserProfileModel, UserProfileModelAdmin)

admin.site.unregister(Token)
admin.site.register(Token, TokenModelAdmin)

admin.site.register(local_models.MqttAclTemplateModel, MqttAclTemplateModelAdmin)

admin.site.register(local_models.MqttAclModel, MqttAclModelAdmin)
