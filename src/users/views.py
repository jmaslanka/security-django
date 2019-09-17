from django.core.paginator import Paginator
from django.views.generic import TemplateView


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
