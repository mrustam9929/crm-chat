import datetime
from typing import Optional

from django.conf import settings
from django.core.cache import cache
from keycloak.keycloak_openid import KeycloakOpenID
from loguru import logger

keycloak_openid = KeycloakOpenID(
    server_url=settings.KEYCLOAK_SERVER_URL,
    client_id=settings.KEYCLOAK_CLIENT_ID,
    realm_name=settings.KEYCLOAK_REALM_NAME,
    client_secret_key=settings.KEYCLOAK_CLIENT_SECRET_KEY
)


def get_keycloak_user_info(keycloak_token: str) -> dict | None:
    """
    Вернет информацию о пользователе из KeyCloak
    :param keycloak_token: access token из KeyCloak
    :return: {
    'roles': list, # роль пользователя
    'id': str, # id пользователя в KeyCloak
    'username': str, # логин пользователя
    'name': str, # имя пользователя
    } or None
    """
    try:
        public_key = cache.get('KEYCLOAK_PUBLIC_SECRET_KEY', None)
        if public_key is None:
            public_key = f'-----BEGIN PUBLIC KEY-----\n{keycloak_openid.public_key()}\n-----END PUBLIC KEY-----'
            cache.set('KEYCLOAK_PUBLIC_SECRET_KEY', public_key, timeout=60 * 60 * 24)
        data = keycloak_openid.decode_token(
            keycloak_token,
            key=public_key
        )
        if data['exp'] < int(datetime.datetime.now().timestamp()):
            return None

        return {
            'id': data['sub'],
            'roles': data['realm_access']['roles'],
            'username': data['preferred_username'],
            'name': data.get('name', None),

        }
    except Exception as e:
        logger.error(f'Error get_keycloak_user_info: {e}')
        return None


def get_keycloak_user_roles(token: str) -> list:
    """
    Получение списка ролей пользователя из токена
    :param token: токен
    :return: список ролей
    """
    user_info = get_keycloak_user_info(token)
    if user_info is None:
        return []
    return user_info.get('roles', [])
