from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .models import User
from .forms import (
    RegistrationForm,
    LoginForm,
)


class RegistrationView(CreateView):
    model = User
    form_class = RegistrationForm
    template_name = 'auth/registration.html'
    success_url = reverse_lazy('auth:login')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class LoginView(LoginView):
    form_class = LoginForm
    template_name = 'auth/login.html'
