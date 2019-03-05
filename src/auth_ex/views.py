import pyotp

from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import (
    TemplateView,
    FormView,
)
from django.views.generic.edit import CreateView


from .models import (
    User,
    Log,
    UserOTP,
)
from .forms import (
    RegistrationForm,
    LoginForm,
    MFASetupForm,
    MFACheckForm,
)
from .utils import (
    create_log_entry,
    generate_mfa_codes,
)


@method_decorator(
    sensitive_post_parameters('password1', 'password2'),
    name='dispatch')
class RegistrationView(CreateView):
    model = User
    form_class = RegistrationForm
    template_name = 'auth/registration.html'
    success_url = reverse_lazy('auth:login')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


@method_decorator(
    [never_cache, sensitive_post_parameters('password')],
    name='dispatch')
class LoginView(LoginView):
    form_class = LoginForm
    template_name = 'auth/login.html'

    def form_valid(self, form):
        user = form.get_user()

        create_log_entry(
            log_type=Log.TYPES.login,
            request=self.request,
            user=user,
        )

        auth_login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        email = form.data.get('username', '')
        user = None

        if email:
            user = User.objects.filter(email=email).first()

        create_log_entry(
            log_type=Log.TYPES.invalid_login,
            request=self.request,
            user=user,
        )

        return super().form_invalid(form)


class SettingsView(TemplateView):
    template_name = 'auth/settings.html'
    logs_paginate_by = 8

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)

        paginator = Paginator(
            self.request.user.logs.order_by('-date'),
            self.logs_paginate_by,
        )

        kwargs['logs'] = paginator.get_page(
            self.request.GET.get('logs-page')
        )

        return kwargs


@method_decorator(never_cache, name='dispatch')
class MFAView(FormView):
    template_name = 'auth/mfa.html'

    def get_form_class(self):
        if self.request.user.has_mfa_enabled():
            return MFACheckForm
        return MFASetupForm

    def get_initial(self):
        initial = super().get_initial()

        initial['secret'] = pyotp.random_base32(length=32)
        initial['link'] = pyotp.TOTP(initial['secret']).provisioning_uri(
            self.request.user.email, settings.MFA_APPLICATION_NAME,
        )

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        context = self.get_context_data()

        if self.request.user.has_mfa_enabled():

            if 'disable' in self.request.POST:
                self.request.user.otp.delete()
                create_log_entry(
                    log_type=Log.TYPES.removed_MFA,
                    request=self.request,
                    user=self.request.user,
                )
                return redirect(reverse('auth:mfa'))

            elif 'new_codes' in self.request.POST:
                mfa_codes = generate_mfa_codes()
                self.request.user.otp.recovery_codes = mfa_codes
                self.request.user.otp.save()
                context['message'] = _(
                    'There are your new recovery codes. '
                    'Please write them down and store somewhere safe. '
                    'Each code can be used only once so we advice to '
                    'get new ones each time you use any of them.'
                )
                context['codes'] = mfa_codes
                context['form'] = MFACheckForm()

                create_log_entry(
                    log_type=Log.TYPES.new_codes_MFA,
                    request=self.request,
                    user=self.request.user,
                )
        else:
            mfa_codes = generate_mfa_codes()
            UserOTP.objects.create(
                user=self.request.user,
                secret_key=form.cleaned_data['secret'],
                recovery_codes=mfa_codes,
            )
            context['message'] = _(
                'You have successfully set your MFA. '
                'There are your recovery codes that you can use '
                'instead of generated code in case you lost your device. '
                'Please write them down and store somewhere safe. '
                'Each code can be used only once so we advice to get new '
                'ones each time you use any of them.'
            )
            context['codes'] = mfa_codes
            context['form'] = MFACheckForm()

            create_log_entry(
                log_type=Log.TYPES.added_MFA,
                request=self.request,
                user=self.request.user,
            )

        return render(self.request, self.template_name, context)
