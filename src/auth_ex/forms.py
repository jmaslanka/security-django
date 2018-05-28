from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
)
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from project.utils import is_valid_recaptcha
from .models import User


class RegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
            'email',
            'password1',
            'password2',
            'first_name',
            'last_name',
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        if not self.request or is_valid_recaptcha(self.request):
            return super().clean()

        raise ValidationError(_('Invalid reCAPTCHA. Please try again.'))


class LoginForm(AuthenticationForm):
    custom_error_message = _(
        'Login failed. Note that fields may be case-sensitive.'
    )
    error_messages = {
        'invalid_login': custom_error_message,
        'inactive': custom_error_message,
    }

    def clean(self):
        if not self.request or is_valid_recaptcha(self.request):
            return super().clean()

        raise ValidationError(_('Invalid reCAPTCHA. Please try again.'))
