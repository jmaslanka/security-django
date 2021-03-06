from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as djUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


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


admin.site.register(User, UserAdmin)
