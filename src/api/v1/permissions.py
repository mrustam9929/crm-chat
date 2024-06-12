from rest_framework import permissions

from apps.users.utils import UserRole


class ClientPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == UserRole.CLIENT)


class CuratorPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == UserRole.CURATOR)
