from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as djUserAdmin
from django.utils.translation import gettext_lazy as _

from project.mixins import ReadOnlyAdminMixin
from .models import (
    Log,
    User,
    UserOTP,
)


class UserAdmin(djUserAdmin):
    list_display = (
        'email',
        'get_full_name',
        'is_active',
        'last_login',
        'date_joined',
    )
    search_fields = (
        'email',
        'first_name',
        'last_name',
    )
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login',)

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
            )
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )


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


admin.site.register(User, UserAdmin)
admin.site.register(UserOTP, UserOTPAdmin)
admin.site.register(Log, LogAdmin)
