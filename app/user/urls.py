from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from user import views

app_name = "user"

urlpatterns = [
    path("register/", views.RegistrationView.as_view(), name="register"),
    path("auth/", views.LoginView.as_view(), name="token_obtain"),
    path("oauth/google/", views.GoogleAuth.as_view(), name="oauth_google"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("update/", views.UpdateUserView.as_view(), name="update"),
    path(
        "password/change/", views.ChangePasswordView.as_view(), name="password_change"
    ),
    path(
        "password/reset/confirm/",
        views.ConfirmResetPasswordView.as_view(),
        name="custom_password_reset",
    ),
    path(
        "password/reset/",
        include("django_rest_passwordreset.urls", namespace="password_generate"),
    ),
    path("email/verify/", views.verify_email_view, name="verify_email"),
    path("detail/", views.DetailView.as_view(), name="detail"),
    path("address/", views.AddressView.as_view(), name="address"),
    path("avatar/", views.AvatarView.as_view(), name="avatar"),
    path("", views.ListUsers.as_view(), name="online-users"),
]
