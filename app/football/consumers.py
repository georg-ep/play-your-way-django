import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from user.models import Clients, User

class ChatConsumer(WebsocketConsumer):

    def connect(self):
        user_id = self.scope["url_route"]["kwargs"]["user_id"]
        user = User.objects.filter(id=user_id).first()
        client = Clients.objects.filter(user=user).first()
        if client is not None:
          print("old client exists, deleting them")
          client.delete()
        Clients.objects.create(channel_name=self.channel_name, user=user)
        self.accept()

    def disconnect(self, close_code):
        # Note that in some rare cases (power loss, etc) disconnect may fail
        # to run; this naive example would leave zombie channel names around.
        Clients.objects.filter(channel_name=self.channel_name).delete()
        print("disconnected")

    def chat_message(self, event):
        # Handles the "chat.message" event when it's sent to us.
        self.send(text_data=json.dumps(event["data"]))