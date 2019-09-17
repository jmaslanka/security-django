from django.contrib.admin import AdminSite as djAdminSite

from auth_ex.forms import MFAAdminAuthenticationForm


class AdminSite(djAdminSite):
    login_form = MFAAdminAuthenticationForm
