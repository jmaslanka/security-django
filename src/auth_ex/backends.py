from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend as djModelBackend

from .models import FailedAuthentication


User = get_user_model()


class ModelBackend(djModelBackend):
    """
    Registering failed authentication attempts.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        try:
            user = User._default_manager.get_by_natural_key(username)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing diff
            User().set_password(password)
        else:
            correct_password = user.check_password(password)
            if not correct_password:
                cookie = request.COOKIES.get(settings.DEVICE_COOKIE_NAME) if request else None
                FailedAuthentication.objects.create(
                    user=user,
                    cookie=cookie[:200] if cookie else None,
                )
            elif self.user_can_authenticate(user):
                return user
