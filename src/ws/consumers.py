import datetime

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.core.cache import cache
from loguru import logger

from apps.users.models import UserRole

CURATOR_GROUP_NAME = 'curators'


class WsChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        """Соединение с вебсокетом"""
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
        else:
            await self.update_user_status(is_connect=True)
            if user.role == UserRole.CURATOR:
                await self.channel_layer.group_add(CURATOR_GROUP_NAME, self.channel_name)
                for topic in self.scope['topics']:
                    await self.channel_layer.group_add(topic, self.channel_name)
            await self.accept()

    async def disconnect(self, code):
        user = self.scope['user']
        if user.is_anonymous:
            pass
        else:
            await self.update_user_status(is_connect=False)
            if user.role == UserRole.CURATOR:
                await self.channel_layer.group_discard(CURATOR_GROUP_NAME, self.channel_name)
                for topic in self.scope['topics']:
                    await self.channel_layer.group_discard(topic, self.channel_name)

    async def receive_json(self, content, **kwargs):
        """Получение данных от клиента"""
        try:
            await self.update_user_connection()
            await self.send_json(content)
        except Exception as e:
            logger.exception(e)

    async def send_event(self, event):
        """Отправка события по вебсокету"""
        event_data = {
            'event_type': event['event_type'],
            'data': event['data']
        }
        await self.send_json(event_data)

    async def update_user_status(self, is_connect: bool):
        """
         Добавляет / Удаляет channel_name подключенного пользователя в кэше
        :param is_connect:
        """
        user_key = settings.USER_CHANNELS_CACHE_KEY.format(user_id=self.scope['user'].id)
        data = await cache.aget(user_key, dict())
        if is_connect:
            data[self.channel_name] = int(datetime.datetime.now().timestamp())
            await self.send_status('online')
        else:
            data.pop(self.channel_name, None)
            if not data:
                await self.send_status('offline')
        await cache.aset(user_key, data, timeout=settings.USER_CHANNELS_CACHE_TIMEOUT)

    async def send_status(self, event):
        """Событие обновления статуса пользователя"""
        status = event if isinstance(event, str) else event['status']
        await self.channel_layer.group_send(
            CURATOR_GROUP_NAME,
            {
                'type': 'send.event',
                'event_type': 'update_status',
                'data': {
                    'user_id': self.scope['user'].id,
                    'status': status
                }
            }
        )

    async def new_chat(self, event):
        """Событие новый чат"""
        ws_data = {
            'type': 'send.event',
            'event_type': 'new_chat',
            'data': {
                'chat_type': event['chat_type'],
                'chat_id': event['chat_id'],
            }
        }
        await self.channel_layer.group_send(event['group_name'], ws_data)
        for channel_name in await self.get_user_channels(event['client_id']):
            await self.channel_layer.send(channel_name, ws_data)

    async def new_message(self, event):
        """событие новое сообщение"""
        ws_data = {
            'type': 'send.event',
            'event_type': 'new_message',
            'data': event['message_data']
        }

        await self.channel_layer.group_send(event['group_name'], ws_data)
        for channel_name in await self.get_user_channels(event['client_id']):
            await self.channel_layer.send(channel_name, ws_data)

    async def update_message(self, event):
        """событие куратор обновил сообщение"""
        ws_data = {
            'type': 'send.event',
            'event_type': 'update_message',
            'data': event['message_data']
        }

        await self.channel_layer.group_send(event['group_name'], ws_data)
        for channel_name in await self.get_user_channels(event['client_id']):
            await self.channel_layer.send(channel_name, ws_data)

    async def curator_delete_message(self, event):
        """событие куратор удалил сообщение"""
        ws_data = {
            'type': 'send.event',
            'event_type': 'delete_message',
            'data': {
                'chat_id': event['chat_id'],
                'message_id': event['message_id']
            }
        }

        await self.channel_layer.group_send(event['group_name'], ws_data)
        for channel_name in await self.get_user_channels(event['client_id']):
            await self.channel_layer.send(channel_name, ws_data)

    async def assign_curator(self, event):
        """Назначение чата"""
        await self.channel_layer.group_send(
            event['group_name'],
            {
                'type': 'send.event',
                'event_type': 'assign_curator',
                'data': {
                    'chat_id': event['chat_id'],
                    'curator_id': event['curator_id']
                }
            }
        )

    async def update_chat_status(self, event):
        """Статус чата"""
        ws_data = {
            'type': 'send.event',
            'event_type': 'update_chat_status',
            'data': {
                'chat_id': event['chat_id'],
                'status': event['status']
            }
        }

        await self.channel_layer.group_send(event['group_name'], ws_data)

        for channel_name in await self.get_user_channels(event['client_id']):
            await self.channel_layer.send(channel_name, ws_data)

    async def read_chat_message(self, event):
        """Прочитанное сообщение"""
        ws_data = {
            'type': 'send.event',
            'event_type': 'read_chat_message',
            'data': {
                'chat_id': event['chat_id'],
                'last_message_id': event['last_message_id'],
                'user_id': event['user_id']
            }
        }
        if self.scope['user'].role == UserRole.CLIENT:
            await self.channel_layer.group_send(event['group_name'], ws_data)
        else:
            for channel_name in await self.get_user_channels(event['client_id']):
                await self.channel_layer.send(channel_name, ws_data)

    async def get_user_channels(self, user_id: int) -> list:
        """Получение каналов пользователя"""
        user_channels = await self.get_user_connections(user_id)
        return list(user_channels.keys())

    async def update_user_connection(self) -> None:
        connections = await self.get_user_connections(self.scope['user'].id)
        connections[self.channel_name] = int(datetime.datetime.now().timestamp())
        cache_key = settings.USER_CHANNELS_CACHE_KEY.format(user_id=self.scope['user'].id)
        await cache.aset(cache_key, connections, timeout=settings.USER_CHANNELS_CACHE_TIMEOUT)

    @staticmethod
    async def get_user_connections(user_id: int) -> dict:
        """Получение подключений пользователя"""
        cache_key = settings.USER_CHANNELS_CACHE_KEY.format(user_id=user_id)
        return await cache.aget(cache_key, dict())
