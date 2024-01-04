import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.id = self.scope['url_route']['kwargs']['course_id']  # извлекаем course_id из маршрута url
        self.room_group_name = f'chat_{self.id}'  # имя чата с id курса
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()  # принять соединение

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(  # покинуть группу (чат)
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):  # получить сообщение из WebSocker и отправить его же назад
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        now = timezone.now()

        await self.channel_layer.group_send(  # отправка сообщения в группу
            self.room_group_name,
            {
                'type': 'chat_message',  # тип события с именем метода
                'message': message,
                'user': self.user.username,
                'datetime': now.isoformat(),
            }
        )

    async def chat_message(self, event):  # получить сообщение из чата
        await self.send(text_data=json.dumps(event))  # отправить в веб-сокет
