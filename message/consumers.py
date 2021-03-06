from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
import base64
from django.core.files.base import ContentFile
from .models import *
from account.models import *


class ChatRoomConsumer(WebsocketConsumer):
    
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        
        self.accept()
    
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    
    def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        email = data['email']
        receiver_id = data['receiver_id']
        msgtype = data['type']
        author = User.objects.get(email=email)
        if OneToOne.objects.filter(user1=author, user2_id=receiver_id).exists():
            onetoone = OneToOne.objects.get(user1=author, user2_id=receiver_id)
        elif OneToOne.objects.filter(user1=receiver_id,user2_id = author).exists():
            onetoone =  OneToOne.objects.get(user1=receiver_id, user2_id =author)
        else:
            onetoone = OneToOne.objects.create(user1 = author, user2_id = receiver_id, room_name=self.room_name)
        if msgtype == 'image':
            format, imgstr = message.split(';base64,')
            ext1 = format.split('/')[-1]
            imageurl = ContentFile(base64.b64decode(imgstr), name=msgtype + '.' + ext1)
            Messages.objects.create(sender=author, receiver_id = receiver_id, onetoone=onetoone, msg_type=msgtype, image = imageurl)
        else:
            Messages.objects.create(sender=author, receiver_id=receiver_id, onetoone=onetoone, msg_type = msgtype, message=message)
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'chat_message',
                'msgtype':msgtype,
                'message':message,
                'email':email,
            }
        )
    
    def chat_message(self, event):
        message = event['message']
        email = event['email']
        msgtype = event['msgtype']
        async_to_sync(
            self.send(text_data=json.dumps({
                'message':message,
                'email':email,
                'msgtype':msgtype,
            }))
        )