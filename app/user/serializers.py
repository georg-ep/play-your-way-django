from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import ugettext_lazy as _

from celery import current_app as celery_app

from hashids import Hashids

import settings
from core import response, exception
from user.models import User, Address


def raise_400(detail):
    raise ValidationError(code=400, detail=detail)


def verify_email(request):
    token = request.data.get("token")

    if not token:
        raise exception.get(ValidationError, _("Token not found"))

    hashids = Hashids(
        salt=settings.EMAIL_HASH_SALT,
        min_length=settings.EMAIL_HASH_MIN_LEN,
        alphabet=settings.EMAIL_HASH_ALPHABET,
    )
    hash_tuple = hashids.decode(token)

    if len(hash_tuple) < 1:
        raise exception.get(ValidationError, _("Wrong token"))

    _id = hash_tuple[0]
    user = User.objects.filter(id=_id).first()

    if not user:
        raise exception.get(ValidationError, _("User not found"))

    user.is_email_verified = True
    user.save()
    return response.ok()


def send_verify_email(request):
    if not request.user.is_authenticated:
        return response.unauthorized()

    celery_app.send_task("send_verify_email", kwargs={"user_id": request.user.id})

    return response.ok()


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """

    password = serializers.CharField(write_only=True)
    email = serializers.CharField(write_only=True)

    access = serializers.SerializerMethodField()
    refresh = serializers.SerializerMethodField()

    def get_access(self, obj: User) -> str:
        """
        Returns user access token for authentication
        """
        refresh_token = RefreshToken.for_user(obj)
        return str(refresh_token.access_token)

    def get_refresh(self, obj: User) -> str:
        """
        Returns user refresh token for authentication
        """
        refresh_token = RefreshToken.for_user(obj)
        return str(refresh_token)

    def create(self, validated_data: dict) -> User:
        """
        Creates and saves user from validated data
        :param validated_data: dict of user parameters
        :return: created user
        """
        validated_data["email"] = validated_data["email"].lower()
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        try:
            user.save()
        except Exception:
            raise ValidationError(_("Already registered"))

        celery_app.send_task("send_verify_email", kwargs={"user_id": user.id})
        return user

    class Meta:
        model = User
        fields = (
            "email",
            "access",
            "refresh",
            "password",
        )


class AddressSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = self.context.get("request").user
        address = Address.objects.filter(user=user).first()

        if address:
            raise exception.get(
                serializers.ValidationError, _("User already have an address")
            )

        validated_data.update({"user": user})
        return super().create(validated_data)

    class Meta:
        model = Address
        exclude = ("user",)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "name")


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "name", "surname")


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(
        write_only=True, allow_null=False, allow_blank=False
    )
    new_password = serializers.CharField(
        write_only=True, allow_blank=False, allow_null=False
    )

    def create(self, validated_data: dict) -> User:
        old_password = validated_data.get("old_password")
        new_password = validated_data.get("new_password")

        user = self.context.get("request").user

        if not user.check_password(old_password):
            raise_400(_("Invalid old password"))

        user.set_password(new_password)
        user.save()
        return user

    class Meta:
        model = User
        fields = ("old_password", "new_password")


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        attrs["email"] = attrs["email"].lower()
        return super().validate(attrs)


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("avatar",)
