from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    LoginView,
    MFAView,
    RegistrationView,
    SettingsView,
)


app_name = 'auth_ex'

urlpatterns = [
    path('signup/', RegistrationView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('settings/mfa/', MFAView.as_view(), name='mfa'),
]
