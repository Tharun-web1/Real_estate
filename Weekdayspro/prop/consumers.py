# prop/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatMessage

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'
        self.user = self.scope["user"]

        # Join room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # 🔵 Set user online
        await self.set_online(True)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # 🔴 Set offline
        await self.set_online(False)

    # =========================
    # RECEIVE MESSAGE FROM FRONTEND
    # =========================
    async def receive(self, text_data):
        data = json.loads(text_data)

        # SEND MESSAGE
        if data.get("type") == "message":
            message = data["message"]

            msg = await self.save_message(message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': msg.message,
                    'sender': self.user.username,
                    'message_id': msg.id
                }
            )

        # READ RECEIPT
        elif data.get("type") == "read":
            await self.mark_as_read()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'read_update',
                    'reader': self.user.username
                }
            )

    # =========================
    # SEND MESSAGE TO FRONTEND
    # =========================
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender': event['sender'],
            'message_id': event['message_id']
        }))

    async def read_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read',
            'reader': event['reader']
        }))

    # =========================
    # DATABASE FUNCTIONS
    # =========================
    @database_sync_to_async
    def save_message(self, message):
        chat = ChatRoom.objects.get(id=self.chat_id)
        return ChatMessage.objects.create(
            chat=chat,
            sender=self.user,
            message=message,
            is_sent=True,
            is_delivered=True
        )

    @database_sync_to_async
    def mark_as_read(self):
        ChatMessage.objects.filter(
            chat_id=self.chat_id
        ).exclude(sender=self.user).update(is_read=True)

    @database_sync_to_async
    def set_online(self, status):
        self.user.is_online = status
        self.user.save()