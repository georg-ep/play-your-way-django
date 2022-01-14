from django_rest_passwordreset.models import ResetPasswordToken

from celery import shared_task

from user import models as user_models
from mail.mail import MailsApp


@shared_task(name="send_verify_email")
def send_verify_email_task(user_id):
    user = user_models.User.objects.filter(id=user_id).first()
    if user is None:
        return

    mail = MailsApp().verify_email(user)
    mail.send()

    if mail.error_message:
        print(mail.error_message)


@shared_task(name="send_reset_password_email")
def send_reset_password_email_task(reset_token_id):
    reset_token = ResetPasswordToken.objects.filter(id=reset_token_id).get()

    if reset_token is None:
        return

    mail = MailsApp().password_reset_mail(reset_token)
    mail.send()

    if mail.error_message:
        print(mail.error_message)
