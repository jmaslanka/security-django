from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView

from project.utils import is_valid_recaptcha
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

    def post(self, request, *args, **kwargs):
        if is_valid_recaptcha(request):
            return super().post(request, *args, **kwargs)

        raise ValidationError(_('Invalid reCAPTCHA. Please try again.'))


class LoginView(LoginView):
    form_class = LoginForm
    template_name = 'auth/login.html'

    def post(self, request, *args, **kwargs):
        if is_valid_recaptcha(request):
            return super().post(request, *args, **kwargs)

        raise ValidationError(_('Invalid reCAPTCHA. Please try again.'))
