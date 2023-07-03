import json
from asgiref.sync import sync_to_async

from channels.auth import login, logout
from channels.generic.websocket import AsyncWebsocketConsumer
import django
django.setup()
from . models import Message


class ChatConsumer(AsyncWebsocketConsumer):


    async def connect(self):

        user = self.scope['user']

        if user.is_authenticated:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            # self.room_group_name = 'chat_%s' % self.room_name
            self.room_group_name = f"chat_{self.room_name}"


            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

        else:
            await self.send({"close": True})

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):


        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        profile_pic = text_data_json['profile_pic']
        room = text_data_json['room']


        await self.save_message(message, username, profile_pic, room)


        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'profile_pic': profile_pic,
                'room': room,
            }
        )

    async def chat_message(self, event):

        message = event['message']
        username = event['username']
        profile_pic = event['profile_pic']
        room = event['room']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'profile_pic': profile_pic,
            'room': room,
        }))

    @sync_to_async
    def save_message(self, message, username, profile_pic, room):
        Message.objects.create(
            message_content=message, username=username, profile_pic=profile_pic, room=room)
