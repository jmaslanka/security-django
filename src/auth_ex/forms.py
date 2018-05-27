from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
)
from django.utils.translation import gettext_lazy as _

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


class LoginForm(AuthenticationForm):
    custom_error_message = _(
        'Login failed. Note that fields may be case-sensitive.'
    )
    error_messages = {
        'invalid_login': custom_error_message,
        'inactive': custom_error_message,
    }
