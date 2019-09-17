from pyotp import TOTP

from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
)
from django import forms
from django.utils.translation import gettext_lazy as _
from django.views.decorators.debug import sensitive_variables

from config.utils import is_valid_recaptcha
from .utils import is_valid_mfa_code, validate_device_cookie


User = get_user_model()


class RegistrationForm(UserCreationForm):
    error_messages = {
        **UserCreationForm.error_messages,
        'invalid_recaptcha': _('Invalid reCAPTCHA response.'),
    }

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

    def get_invalid_captcha_error(self):
        return forms.ValidationError(
            self.error_messages['invalid_recaptcha'],
            code='invalid_recaptcha',
        )

    def clean(self):
        if not self.request or is_valid_recaptcha(self.request):
            return super().clean()

        raise self.get_invalid_captcha_error()


class LoginForm(AuthenticationForm):
    code = forms.RegexField(
        label=_('OTP code'),
        required=False,
        regex=r'^[0-9]{6}$|^[a-zA-Z0-9]{10}$',
    )

    custom_error_message = _(
        'Login failed. Note that fields may be case-sensitive.'
    )
    error_messages = {
        'invalid_login': custom_error_message,
        'inactive': custom_error_message,
        'invalid_recaptcha': _('Invalid reCAPTCHA response.'),
        'throttled_login': _(
            'There were too many unsuccessful login attempts, please try '
            'again later.'
        ),
        'invalid_mfa': _(
            'Invalid one-time password code.'
        )
    }

    def get_invalid_captcha_error(self):
        return forms.ValidationError(
            self.error_messages['invalid_recaptcha'],
            code='invalid_recaptcha',
        )

    def get_throttled_login_error(self):
        return forms.ValidationError(
            self.error_messages['throttled_login'],
            code='throttled_login',
        )

    def get_invalid_mfa_error(self):
        return forms.ValidationError(
            self.error_messages['invalid_mfa'],
            code='invalid_mfa',
        )

    @sensitive_variables('password')
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        code = self.cleaned_data.get('code')

        if username and password:
            if not validate_device_cookie(self.request, username):
                raise self.get_throttled_login_error()

            if not is_valid_recaptcha(self.request):
                raise self.get_invalid_captcha_error()

            self.user_cache = authenticate(
                self.request, username=username, password=password)

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                if not is_valid_mfa_code(self.user_cache, code):
                    raise self.get_invalid_mfa_error()

                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class MFAAdminAuthenticationForm(AdminAuthenticationForm, LoginForm):
    pass


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

    error_messages = {
        'mfa_set_up': _('You already have MFA set up.'),
        'invalid_mfa': _('Invalid one-time password code.'),
    }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def get_mfa_set_up_error(self):
        return forms.ValidationError(
            self.error_messages['mfa_set_up'],
            code='mfa_set_up',
        )

    def get_invalid_mfa_error(self):
        return forms.ValidationError(
            self.error_messages['invalid_mfa'],
            code='invalid_mfa',
        )

    def clean(self):
        super().clean()

        if self.errors:
            return

        if self.user.has_mfa_enabled():
            raise self.get_mfa_set_up_error()

        totp = TOTP(self.cleaned_data.get('secret', ''))

        if totp.verify(self.cleaned_data.get('code')):
            return

        raise self.get_invalid_mfa_error()


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

    error_messages = {
        'invalid_mfa': _('Invalid one-time password code.'),
    }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def get_invalid_mfa_error(self):
        return forms.ValidationError(
            self.error_messages['invalid_mfa'],
            code='invalid_mfa',
        )

    def clean(self):
        super().clean()

        if not self.errors and not is_valid_mfa_code(
                self.user,
                self.cleaned_data.get('code')):
            raise self.get_invalid_mfa_error()
