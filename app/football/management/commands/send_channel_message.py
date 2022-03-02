from django.core.management.base import BaseCommand
from football import consumers

class Command(BaseCommand):
    help = "test"
    def handle(self, *args, **options):
      chat = consumers.ChatConsumer()
      print(chat.__dict__)
      # chat.chat_message({"message": "test"})
