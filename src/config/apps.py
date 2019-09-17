from django.contrib.admin.apps import AdminConfig as djAdminConfig


class AdminConfig(djAdminConfig):
    default_site = 'config.admin.AdminSite'
