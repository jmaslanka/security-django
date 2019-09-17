from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _

from config.mixins import ReadOnlyAdminMixin
from .models import Log, UserOTP, FailedAuthentication


class UserOTPAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recovery_codes_count',
        'created',
    )
    list_select_related = ('user',)
    search_fields = (
        'user__id',
        'user__email',
        'user__last_name',
    )

    def recovery_codes_count(self, obj):
        return len(obj.recovery_codes)
    recovery_codes_count.short_description = _('Recovery codes')


class LogAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = (
        'type',
        'user',
        'date',
        'ip',
        'location',
    )
    list_filter = ('type',)
    list_select_related = ('user',)
    search_fields = (
        'user__id',
        'user__email',
        'user__last_name',
        'ip',
        'location',
    )
    ordering = ('-date',)


class IsCookieFilter(SimpleListFilter):
    title = _('Has cookie')
    parameter_name = 'is_cookie'

    def lookups(self, request, model_admin):
        return [(1, _('Yes')), (0, _('No'))]

    def queryset(self, request, queryset):
        value = self.value()
        if value in ('0', '1'):
            return queryset.filter(cookie__isnull=(not int(value)))

        return queryset.all()


class FailedAuthenticationAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'date', 'is_cookie',)
    list_filter = (IsCookieFilter, 'date',)
    search_fields = (
        'user__id',
        'user__email',
        'user__last_name',
        'cookie',
    )

    def is_cookie(self, obj):
        return bool(obj.cookie)
    is_cookie.short_description = _('Cookie')
    is_cookie.boolean = True


admin.site.register(FailedAuthentication, FailedAuthenticationAdmin)
admin.site.register(UserOTP, UserOTPAdmin)
admin.site.register(Log, LogAdmin)
