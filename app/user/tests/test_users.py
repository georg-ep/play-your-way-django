from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core import mail

from rest_framework import status
from rest_framework.test import APIClient
from django_rest_passwordreset.models import ResetPasswordToken

RESISTER_USER_URL = reverse('user:register')
AUTH_USER_URL = reverse('user:token_obtain')
REFRESH_TOKEN_URL = reverse('user:token_refresh')
VALIDATE_TOKEN_URL = reverse('user:password_reset:reset-password-validate')
PASSWORD_RESET_URL = reverse('user:password_reset:reset-password-request')
PASSWORD_RESET_CONFIRM_URL = reverse('user:password_reset:reset-password-confirm')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class UserApiTests(TestCase):
    """Test the users API. For coverage use: coverage run --omit=*/migrations/* manage.py test user"""

    def setUp(self):
        self.client = APIClient()

    # User registration tests
    def test_user_exists(self):
        """Test creating user that already exists fails"""
        payload = {
            'email': 'novak@pfld.cz',
            'password': '12345678',
        }
        create_user(**payload)
        response = self.client.post(RESISTER_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_was_registered(self):
        """Test that user has been successfully registered"""
        payload = {
            'email': 'novak@pfld.cz',
            'password': '12345678',
        }
        response = self.client.post(RESISTER_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertIsNotNone(user.password)

    def test_register_missing_password(self):
        """Test creating user with empty password"""
        payload = {
            'email': 'novak@pfld.cz',
            'password': '',
        }
        response = self.client.post(RESISTER_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertContains(response, '{"password":["This field may not be blank."]}', None, 400)

    def test_register_missing_email(self):
        """Test creating user with empty email"""
        payload = {
            'email': '',
            'password': '12345',
        }
        response = self.client.post(RESISTER_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertContains(response, '{"email":["This field may not be blank."]}', None, 400)

    def test_register_email_exists(self):
        """Test creating user with already registered email"""
        payload = {
            'email': 'novak@pfld.cz',
            'password': '12345',
        }
        create_user(**payload)
        response = self.client.post(RESISTER_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertContains(response, 'email_already_used', None, 400)

    # Authentication token tests
    def test_create_token_for_user(self):
        """Test that a token is created for user"""
        payload = {
            'email': 'novak@pfld.cz',
            'password': '12345678',
        }
        create_user(**payload)
        response = self.client.post(AUTH_USER_URL, payload)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that a token is not created if invalid credentials are given"""
        create_user(email='novak@pfld.cz', password='12345678')
        payload = {
            'email': 'novak@pfld.cz',
            'password': 'wrong_password',
        }
        response = self.client.post(AUTH_USER_URL, payload)
        self.assertNotIn('refresh', response.data)
        self.assertNotIn('access', response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exists"""
        payload = {
            'email': 'novak@pfld.cz',
            'password': '12345678',
        }
        response = self.client.post(AUTH_USER_URL, payload)
        self.assertNotIn('refresh', response.data)
        self.assertNotIn('access', response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_missing_password(self):
        """Test that password is required"""
        payload = {
            'email': 'novak@pfld.cz',
            'password': '',
        }
        response = self.client.post(AUTH_USER_URL, payload)
        self.assertNotIn('refresh', response.data)
        self.assertNotIn('access', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_username(self):
        """Test that email is required"""
        payload = {
            'email': '',
            'password': '54576',
        }
        response = self.client.post(AUTH_USER_URL, payload)
        self.assertNotIn('refresh', response.data)
        self.assertNotIn('access', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_token_success(self):
        """Test token is refreshed successfully"""
        payload = {
            'email': 'novak@pfld.cz',
            'password': '54576',
        }
        user = create_user(**payload)
        response = self.client.post(AUTH_USER_URL, payload)
        refresh_token = response.data['refresh']

        payload = {
            'refresh': refresh_token
        }
        response = self.client.post(REFRESH_TOKEN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_refresh_token_invalid_token(self):
        """Test invalid refresh token"""
        payload = {
            'email': 'novak@pfld.cz',
            'password': '54576',
        }
        user = create_user(**payload)
        response = self.client.post(AUTH_USER_URL, payload)
        refresh_token = response.data['refresh']

        payload = {
            'refresh': refresh_token[:-1]
        }
        response = self.client.post(REFRESH_TOKEN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertContains(response, 'Token is invalid or expired', None, 401)

    def test_refresh_token_empty(self):
        """Test empty refresh token"""
        payload = {
            'refresh': ''
        }
        response = self.client.post(REFRESH_TOKEN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertContains(response, '{"refresh":["This field may not be blank."]}', None, 400)

    # Password reset tests
    def test_password_reset_invalid_email(self):
        """Test that password reset fails if email is invalid"""
        payload = {
            'email': 'novak@pfld.cz',
            'password': '54576',
        }
        create_user(**payload)
        new_payload = {
            'email': 'dummy@pxfld.cz'
        }
        response = self.client.post(PASSWORD_RESET_URL, new_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertContains(response, 'There is no active user associated with this e-mail address or the '
                                      'password can not be changed', None, 400)

    def test_password_reset_token_generated(self):
        """Test that reset token mail is generated"""
        payload = {
            'email': 'novak@pfld.cz',
            'password': '54576',
        }
        user = create_user(**payload)
        del payload['password']

        # Create token and send email
        response = self.client.post(PASSWORD_RESET_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get token
        token = user.password_reset_tokens.get()
        self.assertIn(token.key, mail.outbox[0].body)

    def test_password_reset_token_is_valid(self):
        """Test password reset token is valid"""
        payload = {
            'email': 'novak@pfld.cz',
            'password': '54576',
        }
        user = create_user(**payload)
        key = ResetPasswordToken.generate_key()
        user.password_reset_tokens.create(key=key)
        token_payload = {
            'token': key
        }
        response = self.client.post(VALIDATE_TOKEN_URL, token_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_token_is_invalid(self):
        """Test password reset token is invalid"""
        payload = {
            'email': 'novak@pfld.cz',
            'password': '54576',
        }
        user = create_user(**payload)
        key = ResetPasswordToken.generate_key()
        user.password_reset_tokens.create(key=key)
        token_payload = {
            'token': 'sdgfgdf'
        }
        response = self.client.post(VALIDATE_TOKEN_URL, token_payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_password_reset_token_is_empty(self):
        """Test password reset token is empty"""
        payload = {
            'token': ''
        }
        response = self.client.post(VALIDATE_TOKEN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertContains(response, '{"token":["This field may not be blank."]}', None, 400)

    def test_password_change_success(self):
        """Test password changed successfully"""
        user = create_user(**{
            'email': 'novak@pfld.cz',
            'password': '54576',
        })
        key = ResetPasswordToken.generate_key()
        user.password_reset_tokens.create(key=key)
        payload = {
            'token': key,
            'password': 'sgfgfgfd'
        }
        response = self.client.post(PASSWORD_RESET_CONFIRM_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_change_invalid_token(self):
        """Test sending invalid token for password change"""
        user = create_user(**{
            'email': 'novak@pfld.cz',
            'password': '54576',
        })
        key = ResetPasswordToken.generate_key()
        user.password_reset_tokens.create(key=key)
        payload = {
            'token': key + '1',  # Making invalid key
            'password': 'sgfgfgfd'
        }
        response = self.client.post(PASSWORD_RESET_CONFIRM_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_password_change_empty_token(self):
        """Test sending empty token for password change"""
        user = create_user(**{
            'email': 'novak@pfld.cz',
            'password': '54576',
        })
        key = ResetPasswordToken.generate_key()
        user.password_reset_tokens.create(key=key)
        payload = {
            'token': '',
            'password': 'sgfgfgfd'
        }
        response = self.client.post(PASSWORD_RESET_CONFIRM_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertContains(response, '{"token":["This field may not be blank."]}', None, 400)

    def test_password_change_empty_password(self):
        """Test sending empty new password for password change"""
        user = create_user(**{
            'email': 'novak@pfld.cz',
            'password': '54576',
        })
        key = ResetPasswordToken.generate_key()
        user.password_reset_tokens.create(key=key)
        payload = {
            'token': key,
            'password': ''
        }
        response = self.client.post(PASSWORD_RESET_CONFIRM_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertContains(response, '{"password":["This field may not be blank."]}', None, 400)
