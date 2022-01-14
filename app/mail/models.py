from django.contrib.postgres.fields import ArrayField
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core import mail as django_mail
from django.conf import settings


class SmtpServer(models.Model):
    """Model for SMTP connection to send emails"""
    host = models.CharField(max_length=255, verbose_name=_('Server connection'))
    port = models.IntegerField(verbose_name=_('Connection port'))
    username = models.CharField(max_length=255, verbose_name=_('User connection name'))
    password = models.CharField(max_length=255, verbose_name=_('Connection password'))
    use_tls = models.BooleanField(max_length=255, verbose_name=_('Is connection TLS?'))
    fail_silently = models.BooleanField(
        verbose_name=_('Fail silently for SMTP connection'),
        default=True,
    )
    from_email = models.CharField(max_length=255, verbose_name=_('Email from'), null=True)
    default = models.BooleanField(default=False, verbose_name=_('Is default connection'))

    def __str__(self):
        return f"{self.host}, {self.username}"

    class Meta:
        verbose_name = _('Smtp server')
        verbose_name_plural = _('Smtp servers')


class AsyncMail(models.Model):
    """Custom mail model. Can be sent immediately or asynchronously using command async_mails_batch"""
    STATUS_NEW = 1
    STATUS_PENDING = 2
    STATUS_FAIL = 3
    STATUS_DONE = 4

    PRIORITY_HEIGHT = 1
    PRIORITY_LESS = 2

    STATUSES = (
        (STATUS_NEW, _('Email will be sending')),
        (STATUS_PENDING, _('Email will be sending')),
        (STATUS_FAIL, _('Email sending is fail')),
        (STATUS_DONE, _('Email is done')),
    )
    subject = models.CharField(max_length=255, verbose_name=_('Subject'))
    body = models.TextField(max_length=255, verbose_name=_('Body email'))
    from_email = models.CharField(max_length=255, verbose_name=_('From email'))
    reply_to = models.CharField(max_length=255, null=True, default=None, verbose_name=_('Reply to'))
    to_emails = ArrayField(base_field=models.CharField(max_length=255))
    created = models.DateTimeField(verbose_name=_('Created'), auto_now=True, editable=False)
    send_time = models.DateTimeField(verbose_name=_('Send time'), auto_now=False, editable=False, null=True)
    status = models.IntegerField(verbose_name=_('Status'), choices=STATUSES, default=STATUS_NEW)
    error_message = models.TextField(verbose_name=_('Error message'), null=True)
    connection = models.ForeignKey(SmtpServer, on_delete=models.SET_NULL, null=True)
    priority = models.IntegerField(verbose_name=_('Sending priority'), default=PRIORITY_LESS)
    hash = models.CharField(verbose_name=_('Hash email string'), null=True, editable=False, max_length=255)
    body_text = models.TextField(verbose_name=_('Text version'), null=True)
    batch = models.BooleanField(verbose_name=_('Send email in batch process'), null=True, default=False)

    def send(self):
        connection = EmailBackend(
            host=self.connection.host,
            port=self.connection.port,
            username=self.connection.username,
            password=self.connection.password,
            use_tls=self.connection.use_tls,
            fail_silently=self.connection.fail_silently
        )

        print(f'host: {connection.host}\n'
              f'port: {connection.port}\n'
              f'username: {connection.username}\n'
              f'password: {connection.password}\n'
              f'use_tls: {connection.use_tls}\n'
              f'from_email: {self.from_email}')

        if settings.EMAIL_BACKEND == settings.TEST_EMAIL_BACKEND:
            # "Virtual" connection for email testing
            connection = None

        if not self.reply_to:
            self.reply_to = self.from_email

        msg = EmailMultiAlternatives(
            self.subject,
            self.body_text,
            self.from_email,
            self.to_emails,
            connection=connection,
            reply_to=[self.reply_to]
        )
        msg.attach_alternative(self.body, "text/html")

        try:
            self.status = self.STATUS_DONE
            self.error_message = None
            self.batch = False
            self.save()
            return msg.send()
        except Exception as exception:
            self.error_message = exception
            self.status = self.STATUS_FAIL
            self.save()
        self.send_time = timezone.now()

    def __str__(self):
        return f"{self.subject}, {self.to_emails}"

    class Meta:
        verbose_name = _('Async mail')
        verbose_name_plural = _('Async mails')
