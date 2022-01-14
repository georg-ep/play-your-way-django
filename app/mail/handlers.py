from hashids import Hashids

from django.urls import reverse
from django_rest_passwordreset.models import ResetPasswordToken
from django.utils.translation import ugettext_lazy as _

import settings
from user.models import User


def password_reset_handler(reset_password_token: ResetPasswordToken) -> dict:
    """Generates replacement dict for password_reset_mail"""
    sections = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.get_username(),
        'email': reset_password_token.user.email,
        'code': reset_password_token.key,
        'text': _('Please use this code for reset password:\n%(code)s\n') % {'code': reset_password_token.key}
    }
    return sections


def verify_email_handler(user: User) -> dict:
    """Generates replacement dict for verify_email"""
    hashids = Hashids(salt=settings.EMAIL_HASH_SALT,
                      min_length=settings.EMAIL_HASH_MIN_LEN,
                      alphabet=settings.EMAIL_HASH_ALPHABET)
    token = hashids.encode(user.id)
    url = settings.FRONTEND_VERIFY_EMAIL_URL + f"?token={token}"
    sections = {
        'current_user': user,
        'email': user.email,
        'url': url,
        'text': _('Please use this url for verify email:\n%(url)s\n') % {'url': url}
    }
    return sections
