import datetime
from typing import Optional

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, AbstractUser
from django.core.cache import cache
from django.db import models

from apps.users.utils import UserRole


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, **extra_fields):
        user = self.model(**extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.CHAT_DASHBOARD_ADMIN)

        if not username:
            raise ValueError('User must have an username')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        extra_fields['username'] = username
        user = self._create_user(**extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_keycloak_user(self, username: str, role: str, name: str | None, **kwargs):
        user = self._create_user(
            username=username,
            role=role,
            name=name
        )
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=150, unique=True, null=True, verbose_name='Логин'
    )
    role = models.CharField(
        max_length=255, choices=UserRole.choices, verbose_name='Роль',
    )
    name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name='Имя'
    )
    is_staff = models.BooleanField(
        default=False,
    )

    USERNAME_FIELD = 'username'
    objects = UserManager()

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_online(self) -> bool:
        return bool(self.get_ws_connections())

    def get_ws_connections(self) -> dict:
        user_key = settings.USER_CHANNELS_CACHE_KEY.format(user_id=self.pk)
        data = cache.get(user_key, dict())
        if data:
            tm = int(datetime.datetime.now().timestamp())
            data = {k: v for k, v in data.items() if v + settings.USER_CHANNELS_CACHE_TIMEOUT >= tm}
            cache.set(user_key, data, settings.USER_CHANNELS_CACHE_TIMEOUT)
        return data

    def get_ws_channels(self) -> list:
        return list(self.get_ws_connections().keys())

    def check_keycloak_update(self, keycloak_user_data: dict) -> None:
        update_fields = []

        if self.name != keycloak_user_data['name']:
            self.name = keycloak_user_data['name']
            update_fields.append('name')

        role = UserRole.get_keycloak_user_role(keycloak_user_data['roles'])
        if role and self.role != role:
            self.role = role
            update_fields.append('role')

        if update_fields:
            self.save(update_fields=update_fields)
