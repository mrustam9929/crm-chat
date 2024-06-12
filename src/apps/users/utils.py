from typing import Optional

from django.conf import settings
from django.db import models


class UserRole(models.TextChoices):
    CHAT_DASHBOARD_ADMIN = 'chat_dashboard_admin', 'Администратор чата'
    CLIENT = 'client', 'Клиент'
    CURATOR = 'curator', 'Куратор'

    @staticmethod
    def get_keycloak_user_role(roles: list) -> Optional[str]:
        """
        Вернет роль пользователя
        :param roles: список ролей пользователя из KeyCloak
        :return: str or None
        """
        if settings.KEYCLOAK_CURATOR_ROLE in roles:
            return UserRole.CURATOR
        elif settings.KEYCLOAK_CLIENT_ROLE in roles:
            return UserRole.CLIENT
        return None
