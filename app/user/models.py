from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core import exception
from core.models import safe_file_path
from core.validators import validate_file_size


class UserManager(BaseUserManager):
    """User manager class for creating users and superusers"""

    def create_user(self, email: str, password: str = None, **extra_fields: dict) -> 'User':
        """
        Creates and saves new user
        :param email: user email
        :param password: user password
        :param extra_fields: additional parameters
        :return: created user model
        """
        if not email:
            raise exception.get(ValueError, 'User must have email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email: str, password: str) -> 'User':
        """
        Creates and saves new super user
        :param email: user email
        :param password: user password
        :return: created user model
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(
        max_length=255,
        unique=True,
        error_messages={'unique': "email_already_used"},
        verbose_name = _("Email")
    )
    name = models.CharField(
        default='',
        max_length=64,
        verbose_name=_("Name")
    )
    surname = models.CharField(
        default='',
        max_length=64,
        verbose_name=_("Surname")
    )
    avatar = models.ImageField(
        upload_to=safe_file_path,
        null=True,
        default=None,
        blank=True,
        validators=[validate_file_size],
        verbose_name=_('Avatar'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("Created at")
    )
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name=_("Is email verified?")
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("Is staff?"),
        help_text=_("Use this option for create Staff")
    )
    objects = UserManager()

    USERNAME_FIELD = 'email'


class Address(models.Model):

    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        verbose_name=_('User')
    )

    city = models.CharField(
        default='',
        max_length=64,
        verbose_name=_("City")
    )
    street = models.CharField(
        default='',
        max_length=64,
        verbose_name=_("Street")
    )
    postal_code = models.CharField(
        default='',
        max_length=10,
        verbose_name=_("Postal code")
    )
    state = models.CharField(
        default='',
        max_length=64,
        verbose_name=_("State")
    )
    country = models.CharField(
        default='',
        max_length=64,
        verbose_name=_("Country")
    )
