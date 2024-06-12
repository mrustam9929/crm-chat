from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser

from apps.chat.models import ChatTopic
from apps.users.models import User
from core.libs.keycloak import get_keycloak_user_info


@database_sync_to_async
def get_user(token) -> tuple:
    """
    Вернет пользователя по токену
    :param token: токен кейклока
    :return: User | None
    """
    user_info = get_keycloak_user_info(token)
    if user_info:
        user = User.objects.filter(username=user_info['username']).first()
        user_topics = list(
            ChatTopic.objects.filter(permission__in=user_info['roles']).values_list('permission', flat=True)
        )
    else:
        user = None
        user_topics = []
    return user, user_topics


class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        try:
            token_key = (dict((x.split('=') for x in scope['query_string'].decode().split("&")))).get('token', None)
        except ValueError:
            token_key = None
        if token_key:
            user, topics = await get_user(token_key)
            scope['user'] = AnonymousUser() if user is None else user
            scope['topics'] = topics
        else:
            scope['user'] = AnonymousUser()
            scope['topics'] = []
        return await super().__call__(scope, receive, send)
