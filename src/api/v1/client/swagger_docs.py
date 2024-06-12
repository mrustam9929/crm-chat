from drf_yasg.openapi import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied

from api.v1.client.serializers import ChatMessageListSerializer

DEFAULT_403 = Response(
    description='Нет прав',
    examples={
        'application/json': {
            'detail': PermissionDenied.default_detail
        }
    }
)
DEFAULT_404 = Response(
    description='Чат не найден',
    examples={
        'application/json': {
            'detail': NotFound.default_detail
        }
    }
)

CREATE_CHAT_MESSAGE = {
    status.HTTP_403_FORBIDDEN: DEFAULT_403,
    status.HTTP_404_NOT_FOUND: DEFAULT_404,
    status.HTTP_201_CREATED: ChatMessageListSerializer,
    # status.HTTP_400_BAD_REQUEST: Response(
    #     description='Нельзя удалить автора',
    #     examples={
    #         'application/json': {
    #             'detail': '<Сообщение которое нужно показать пользователю>',
    #         }
    #     }
    # )
}
