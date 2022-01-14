import hashlib
import subprocess

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django_rest_passwordreset.models import ResetPasswordToken

from mail import handlers
from mail.models import SmtpServer, AsyncMail
from settings import EMAIL_RESET_PASSWORD_TEMPLATE, EMAIL_VERIFY_EMAIL_TEMPLATE
from user.models import User


class MailComponent:

    def __init__(self, connection: SmtpServer):
        self.smtp_server = connection

    def from_template(self, **kw) -> (AsyncMail, bool):
        """
        Generate email from template and return mail model

        :param kw: dict of replacements where keys correspond to tags in mail template: greeting, table, button,
            end_text
        :return: create and return mail.models.AsyncMail object
        """
        hash_string = self._hash(**kw)
        assert 'to' in kw.keys()
        assert 'template' in kw.keys()
        assert 'subject' in kw.keys()

        to = [kw['to']] if isinstance(kw['to'], str) else kw['to']

        template = kw['template']
        subject = kw['subject']
        text_message = kw.get('text_message', '')
        data = kw.get('data', {})
        data['logo'] = 'https://storage.googleapis.com/exemplar_email_assets/exemplar-logo.png'
        data['card_bg'] = 'https://storage.googleapis.com/exemplar_email_assets/card-bg.png'
        data['footer_logo'] = 'https://storage.googleapis.com/exemplar_email_assets/exemplar-footer-logo.png'
        priority = kw['priority'] if 'priority' in kw.keys() else AsyncMail.PRIORITY_LESS
        batch = kw['batch'] if 'batch' in kw.keys() else False

        body = render_to_string(template, data)

        from_email = self.smtp_server.from_email \
            if self.smtp_server.from_email != 'apikey' \
            else settings.DEFAULT_EMAIL_FROM

        return AsyncMail.objects.create(
            subject=subject,
            body=body,
            body_text=text_message,
            from_email=from_email,
            reply_to=data.get('reply_to'),
            to_emails=to,
            connection=self.smtp_server,
            priority=priority,
            batch=batch
        ), True

    def _hash(self, **kwargs):
        hash_string = ''.join([f"{v}:{kwargs[v]}" for v in kwargs.keys()])
        return hashlib.md5(hash_string.encode()).hexdigest()


class MailsApp:
    """
    App for creating and sending emails.

    Use desired function to generate the email, e.g. MailsApp().password_reset(...)
    - Or send batch asynchronously after creating all emails MailsApp().send_async_batch()
    - Or send immediately with generated_mail.send()
    """

    DEFAULT_CONNECTION = settings.DEFAULT_EMAIL_CONNECTION

    def _create_model(self, subject: str, sections: dict, to_email: str, template: str) -> AsyncMail:
        """
        Create and return email model object

        :param subject: subject text of the email
        :param sections: dict of replacements for mail template
        :param to_email: where to send email
        :return: creates and returns mail.models.AsyncMail object
        """
        model, created = self._mail_component().from_template(subject=subject,
                                                              to=to_email,
                                                              data=sections,
                                                              text_message=sections['text'],
                                                              batch=True,
                                                              template=template)
        return model

    def password_reset_mail(self, reset_password_token: ResetPasswordToken) -> AsyncMail:
        subject = _("Password Reset for %(project_name)s") % {'project_name': settings.PROJECT_NAME}
        return self._create_model(subject,
                                  handlers.password_reset_handler(reset_password_token),
                                  reset_password_token.user.email,
                                  EMAIL_RESET_PASSWORD_TEMPLATE)

    def verify_email(self, user: User):
        subject = _("Email confirmation for %(project_name)s") % {'project_name': settings.PROJECT_NAME}
        return self._create_model(subject,
                                  handlers.verify_email_handler(user),
                                  user.email,
                                  EMAIL_VERIFY_EMAIL_TEMPLATE)

    def _send_async_batch(self) -> None:
        """
        Send all mails in database with batch=True

        :return: None
        """
        subprocess.Popen(["python", "/app/manage.py", "async_mails_batch"])

    def _mail_component(self) -> MailComponent:
        """
        Create MailComponent

        :return: MailComponent for mail generation
        """
        return MailComponent(self._default_connection())

    def _default_connection(self) -> SmtpServer:
        """
        Return existing or create new default connection

        :return: mail.models.SmtpServer
        """
        model = SmtpServer.objects.filter(default=True).first()
        if model:
            return model
        return SmtpServer.objects.create(**self.DEFAULT_CONNECTION)
