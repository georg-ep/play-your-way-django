from django.db.models.signals import post_save
from django.dispatch import receiver
from bet import models as bet_models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from user.models import User, Clients


@receiver(post_save, sender=bet_models.Bet)
def on_bet_save(sender, created, instance, **kwargs):

    user = User.objects.filter(id=instance.user2_id).first()
    client = Clients.objects.filter(user=user).first()
    if client is not None:
      channel_layer = get_channel_layer()
      channel = client.channel_name

      data = {
        "type": "bet_received",
        "from": instance.user1.email,
        "amount": str(instance.amount),
      }

      async_to_sync(channel_layer.send)(channel, {
          "type": "chat.message",
          "data": data,
      })
