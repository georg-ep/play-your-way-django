from django.test.testcases import TestCase
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.conf import settings

from django_rest_passwordreset.models import ResetPasswordToken

from mail.mail import MailsApp
from mail.models import SmtpServer


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_token():
    """Change this function for custom receiving email"""
    user = create_user(email='vasylchenko.testing@pixelfield.cz', password='0000')
    return user.password_reset_tokens.create(key=ResetPasswordToken.generate_key())


def create_connection(**kwargs):
    DEFAULT_CONNECTION = settings.DEFAULT_EMAIL_CONNECTION
    DEFAULT_CONNECTION.update(kwargs)
    return SmtpServer.objects.create(**DEFAULT_CONNECTION)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
class TestMailApp(TestCase):
    """Tests for mailing app. Run separately from another tests. Beware of spam block as mails are physically sent to
    the user defined in create_token(). Spam block results in 535: authentication failed error."""

    def test_mail_sending_empty_username(self):
        """Test sending with empty username for mail backend"""
        create_connection(username='')
        mail_model = MailsApp().password_reset_mail(create_token())
        mail_model.send()
        self.assertIn('Authentication Required', str(mail_model.error_message))
        self.assertEqual(mail_model.status, mail_model.STATUS_FAIL)

    def test_mail_sending_invalid_credentials(self):
        """Test sending with invalid username/password"""
        create_connection(username='some@gmail.com', password='dgfghghf', from_email='some@gmail.com')
        mail_model = MailsApp().password_reset_mail(create_token())
        mail_model.send()
        self.assertIn('Password not accepted', str(mail_model.error_message))
        self.assertEqual(mail_model.status, mail_model.STATUS_FAIL)

    def test_mail_sending_success(self):
        """Test sending successful mail. Mail is actually delivered at the target email."""
        # Change following according to existing email account
        create_connection(host='smtp.gmail.com',
                          username='vasylchenko.testing@gmail.com',
                          password='Dfvfdvbfkvdfk1214435',
                          from_email='vasylchenko.testing@gmail.com')
        mail_model = MailsApp().password_reset_mail(create_token())
        mail_model.send()
        self.assertIsNone(mail_model.error_message)
        self.assertEqual(mail_model.status, mail_model.STATUS_DONE)
