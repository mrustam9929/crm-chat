from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions

from apps.users.models import User
from apps.users.utils import UserRole
from core.libs.keycloak import get_keycloak_user_info


class KeyCloakAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        keycloak_token = request.META.get('HTTP_AUTHORIZATION')
        if keycloak_token is None:
            raise exceptions.AuthenticationFailed()

        user_info = get_keycloak_user_info(keycloak_token)
        if user_info is None:
            raise exceptions.AuthenticationFailed()

        user = User.objects.filter(username=user_info['username']).first()
        if user is None:
            role = UserRole.get_keycloak_user_role(user_info['roles'])
            if role is None:
                raise exceptions.AuthenticationFailed()
            user = User.objects.create_keycloak_user(
                username=user_info['username'],
                role=role,
                name=user_info['name']
            )
        else:
            user.check_keycloak_update(user_info)
        return user, None
