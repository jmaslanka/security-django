from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import LoginAPIView

app_name = 'auth_ex'

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
