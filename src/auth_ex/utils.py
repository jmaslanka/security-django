import secrets
import string
from pyotp import TOTP

from project.utils import get_client_details
from .models import Log


CHARACTERS = string.ascii_letters + string.digits


def generate_mfa_codes(quantity=5, length=10) -> list:
    return [
        ''.join(secrets.choice(CHARACTERS) for _ in range(length))
        for _ in range(quantity)
    ]


def is_valid_mfa_code(user, code) -> bool:
    if not user.has_mfa_enabled():
        return True

    totp = TOTP(user.otp.secret_key)

    if code == totp.now():
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
