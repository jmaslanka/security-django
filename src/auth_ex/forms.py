from pyotp import TOTP

from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
)
from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from project.utils import is_valid_recaptcha
from .models import User
from .utils import is_valid_mfa_code


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

        raise ValidationError(
            _('Invalid reCAPTCHA. Please try again.')
        )


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

        raise ValidationError(
            _('Invalid reCAPTCHA. Please try again.')
        )


class MFASetupForm(forms.Form):
    link = forms.CharField(
        widget=forms.HiddenInput(),
    )
    secret = forms.CharField(
        widget=forms.HiddenInput(),
    )
    code = forms.RegexField(
        label=_('Code'),
        regex=r'[0-9]{6}',
        error_messages={
            'invalid': _('Enter a valid 6 digit code.'),
        },
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        if self.errors:
            return

        if self.user.has_mfa_enabled():
            raise forms.ValidationError(
                _('You already have MFA set up.')
            )

        totp = TOTP(self.cleaned_data.get('secret', ''))

        if self.cleaned_data.get('code', '') == totp.now():
            return

        raise forms.ValidationError(
            _('Invalid code, please try again.')
        )


class MFACheckForm(forms.Form):
    code = forms.RegexField(
        label=_('Code'),
        regex=r'^[0-9]{6}$|^[a-zA-Z0-9]{10}$',
        error_messages={
            'invalid': _(
                'Enter 6 digit code or 10 characters recovery code.'
            ),
        },
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        if self.errors:
            return

        if is_valid_mfa_code(
                self.user,
                self.cleaned_data.get('code', '')):
            return

        raise forms.ValidationError(
            _('Invalid code, please try again.')
        )
