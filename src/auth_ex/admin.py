from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as djUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    User,
    Log,
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
                'groups', 'user_permissions',
            )
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )


class LogsAdmin(admin.ModelAdmin):
    list_display = (
        'type',
        'user_id',
        'date',
    )
    list_filter = (
        'type',
    )
    search_fields = (
        'user__id',
        'user__email',
        'location',
    )
    ordering = (
        '-date',
    )


admin.site.register(User, UserAdmin)
admin.site.register(Log, LogsAdmin)
