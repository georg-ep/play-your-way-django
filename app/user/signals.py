from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created

from celery import current_app as celery_app


@receiver(reset_password_token_created)
def on_reset_password_token_creation(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    celery_app.send_task(
        "send_reset_password_email",
        kwargs={
            "reset_token_id": reset_password_token.id
        }
    )
