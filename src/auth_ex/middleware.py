from django.conf import settings
from django.urls import reverse


class DeviceCookieMiddleware:
    """
    Set device cookie if request is a successful login.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.login_paths = [
            reverse('auth:login'),
            reverse('admin:login'),
        ]

    def __call__(self, request):
        response = self.get_response(request)

        if request.path in self.login_paths and \
                request.method.lower() == 'post' and \
                request.user.is_authenticated and \
                response.status_code in [200, 302]:
            response.set_signed_cookie(
                settings.DEVICE_COOKIE_NAME,
                request.user.email,
                salt=settings.DEVICE_COOKIE_SALT,
                max_age=settings.DEVICE_COOKIE_AGE,
                secure=settings.CSRF_COOKIE_SECURE,
                samesite='Strict',
                httponly=True,
            )

        return response
