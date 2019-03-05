from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles import views
from django.urls import include, path, re_path
from django.views.static import serve

from .views import HomepageView

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('superuser-panel/', admin.site.urls),

    path('', HomepageView.as_view(), name='homepage'),
    path('auth/', include('auth_ex.urls', namespace='auth')),
]

if settings.DEBUG:
    re_path(r'^static/(?P<path>.*)$', views.serve),
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
