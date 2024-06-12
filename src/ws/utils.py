from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.chat.models import Chat, ChatMessage
from apps.users.models import User
from ws.consumers import CURATOR_GROUP_NAME
from ws.serializers import WsChatMessageEventSerializer


def ws_event_new_chat(chat: Chat, user: User) -> None:
    """
    Отправка события нового чата
    """
    channels = user.get_ws_channels()
    if channels:
        channel_layer = get_channel_layer()
        group_name = chat.topic.permission if chat.topic else CURATOR_GROUP_NAME
        async_to_sync(channel_layer.send)(
            channels[0],
            {
                'type': 'new.chat',
                'chat_id': chat.id,
                'user_id': user.id,
                'client_id': chat.client_id,
                'group_name': group_name,
                'chat_type': chat.chat_type,
            }
        )


def ws_event_new_message(chat_message: ChatMessage, user: User, request) -> None:
    """
    Отправка события нового сообщения
    """
    channels = user.get_ws_channels()
    if channels:
        channel_layer = get_channel_layer()
        chat = chat_message.chat
        group_name = chat.topic.permission if chat.topic else CURATOR_GROUP_NAME
        async_to_sync(channel_layer.send)(
            channels[0],
            {
                'type': 'new.message',
                'message_data': WsChatMessageEventSerializer(chat_message, context={'request': request}).data,
                'group_name': group_name,
                'client_id': chat_message.chat.client_id,
            }
        )


def ws_event_update_message(curator: User, chat_message: ChatMessage, request) -> None:
    """
    Отправка события куратор обновил сообщение
    """
    channels = curator.get_ws_channels()
    if channels:
        channel_layer = get_channel_layer()
        chat = chat_message.chat
        group_name = chat.topic.permission if chat.topic else CURATOR_GROUP_NAME
        async_to_sync(channel_layer.send)(
            channels[0],
            {
                'type': 'update.message',
                'message_data': WsChatMessageEventSerializer(chat_message, context={'request': request}).data,
                'group_name': group_name,
                'client_id': chat_message.chat.client_id,
            }
        )


def ws_event_delete_message(curator: User, chat: Chat, message_id: int, client_id: int):
    """
    Отправка события куратор удалил сообщение
    """

    channels = curator.get_ws_channels()
    if channels:
        channel_layer = get_channel_layer()
        group_name = chat.topic.permission if chat.topic else CURATOR_GROUP_NAME
        async_to_sync(channel_layer.send)(
            channels[0],
            {
                'type': 'curator.delete.message',
                'chat_id': chat.id,
                'message_id': message_id,
                'group_name': group_name,
                'client_id': client_id,
            }
        )


def ws_event_assign_curator(chat: Chat, user: User) -> None:
    """
    Отправка события назначения куратора на чат
    """
    channels = user.get_ws_channels()
    if channels:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(
            channels[0],
            {
                'type': 'assign.curator',
                'chat_id': chat.id,
                'curator_id': chat.curator_id,
                'group_name': chat.topic.permission,
            }
        )


def ws_update_chat_status(chat: Chat, user: User) -> None:
    """
    Отправка события обновления статуса чата
    """
    channels = user.get_ws_channels()
    if channels:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(
            channels[0],
            {
                'type': 'update.chat.status',
                'chat_id': chat.id,
                'status': chat.status,
                'group_name': chat.topic.permission,
                'client_id': chat.client_id,
            }
        )


def ws_read_chat_message(chat: Chat, user: User, message_id: int) -> None:
    channels = user.get_ws_channels()
    if channels:
        channel_layer = get_channel_layer()
        group_name = chat.topic.permission if chat.topic else CURATOR_GROUP_NAME
        async_to_sync(channel_layer.send)(
            channels[0],
            {
                'type': 'read.chat.message',
                'chat_id': chat.pk,
                'last_message_id': message_id,
                'group_name': group_name,
                'client_id': chat.client_id,
                'user_id': user.pk,
            }
        )
