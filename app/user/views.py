from django_rest_passwordreset.serializers import PasswordTokenSerializer
from django.utils.translation import ugettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, filters
from rest_framework.decorators import api_view
from rest_framework.parsers import FileUploadParser
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    ListAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django_rest_passwordreset.views import ResetPasswordConfirm

import requests

from .models import User

from settings import GOOGLE_AUTH_BASE_URL
from user.google_oauth import GoogleUser
from user import serializers
from user.models import Address


class ListUsers(ListAPIView):
    serializer_class = serializers.UserDetailSerializer
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["email"]


class LoginView(TokenObtainPairView):
    serializer_class = serializers.LoginSerializer


class RegistrationView(CreateAPIView):
    serializer_class = serializers.UserRegisterSerializer


class ChangePasswordView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ChangePasswordSerializer


class ConfirmResetPasswordView(ResetPasswordConfirm):
    serializer_class = PasswordTokenSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        status_message = response.data.get("status", None)

        if status_message is None:
            return response

        if status_message == "OK":
            return response

        message_map = {
            "notfound": _("Code is not found."),
            "expired": _("Code has expired."),
        }
        response.data["status"] = message_map[status_message]

        return response


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={"token": openapi.Schema(type=openapi.TYPE_STRING)},
    ),
    operation_description="""
    Verify user email using code from email.
    """,
)
@api_view(["post"])
def verify_email_view(request):
    return serializers.verify_email(request)


class DetailView(RetrieveAPIView):
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class AddressView(CreateAPIView, RetrieveAPIView, UpdateAPIView):
    serializer_class = serializers.AddressSerializer
    permission_classes = [IsAuthenticated]
    allowed_methods = {"POST", "GET", "PATCH"}

    def get_object(self):
        return Address.objects.filter(user=self.request.user).first()


class AvatarView(UpdateAPIView):
    serializer_class = serializers.AvatarSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FileUploadParser]
    allowed_methods = {"PATCH"}

    def get_object(self):
        return self.request.user


class GoogleAuth(APIView):
    serializer_class = serializers.UserDetailSerializer

    def post(self, request):
        base_url = GOOGLE_AUTH_BASE_URL
        token = request.data.get("token", "")
        url = f"{base_url}&access_token={token}"
        res = requests.get(url)
        data = res.json()
        if not "sub" in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = GoogleUser(data).get_user()
        serialized = serializers.UserDetailSerializer(
            user, context={"request": request}
        )
        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        user = self.request.user
        serialized = serializers.UserDetailSerializer(instance=user)
        return Response(serialized.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={"token": openapi.Schema(type=openapi.TYPE_STRING)},
    ),
    operation_description="""
    Verify user email using code from email.
    """,
)
@api_view(["post"])
def verify_email_view(request):
    return serializers.verify_email(request)


@api_view(http_method_names=["post"])
def send_verify_email_view(request):
    return serializers.send_verify_email(request)
