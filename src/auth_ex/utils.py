import secrets
import string
from pyotp import TOTP

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone

from config.utils import get_client_details
from .models import Log, FailedAuthentication


CHARACTERS = string.ascii_letters + string.digits
User = get_user_model()


def generate_mfa_codes(quantity=5, length=10) -> list:
    return [
        ''.join(secrets.choice(CHARACTERS) for _ in range(length))
        for _ in range(quantity)
    ]


def is_valid_mfa_code(user, code) -> bool:
    if not user.has_mfa_enabled():
        return True

    if TOTP(user.otp.secret_key).verify(code):
        return True

    # Checking if one of recovery codes was provided.
    if code in user.otp.recovery_codes:
        user.otp.recovery_codes.remove(code)
        user.otp.save()
        return True

    return False


def create_log_entry(log_type, request, user=None) -> None:
    client = get_client_details(request)
    Log.objects.create(
        user=user,
        type=log_type,
        ip=client['ip'],
        location=client['location'],
        user_agent=client['user_agent'],
    )


def validate_device_cookie(request, email) -> bool:
    """
    Validating device cookie.
    https://www.owasp.org/index.php/Slow_Down_Online_Guessing_Attacks_with_Device_Cookies
    """

    cookie = request.COOKIES.get(settings.DEVICE_COOKIE_NAME)
    user_email = None
    date_period = timezone.now() - timezone.timedelta(
        seconds=settings.DEVICE_COOKIE_PERIOD)

    if cookie:
        user_email = request.get_signed_cookie(
            settings.DEVICE_COOKIE_NAME,
            salt=settings.DEVICE_COOKIE_SALT,
            default=None,
        )

    if user_email == email:
        return User.objects.filter(
            email=email,
        ).annotate(
            failed_attempts=Count(
                'failed_authentications',
                filter=(
                    Q(failed_authentications__cookie=cookie) &
                    Q(failed_authentications__date__gt=date_period)
                )
            )
        ).filter(failed_attempts__lt=settings.DEVICE_COOKIE_TRIES).exists()

    return FailedAuthentication.objects.filter(
        user__email=email,
        cookie=None,
        date__gt=date_period,
    ).count() < settings.DEVICE_COOKIE_TRIES
