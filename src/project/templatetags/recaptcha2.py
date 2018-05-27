from django import template
from django.conf import settings


register = template.Library()


@register.inclusion_tag('auth/recaptcha.html')
def recaptcha():
    return {'public_key': settings.RECAPTCHA_PUBLIC_KEY}
