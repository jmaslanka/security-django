from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles import views
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/', include('auth_ex.urls')),
]

if settings.DEBUG:
    re_path(r'^static/(?P<path>.*)$', views.serve),
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
