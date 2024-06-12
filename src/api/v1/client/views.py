from django.db.models import Max, Prefetch, Q, Count
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, permissions
from rest_framework.exceptions import NotFound
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from api.v1.authentication import KeyCloakAuthentication
from api.v1.client import serializers
from api.v1.client import swagger_docs
from api.v1.client.filters import ChatListFilter
from api.v1.permissions import ClientPermission
from apps.chat.models import ChatTopic, Chat, ChatMessage
from ws.utils import ws_read_chat_message


class TopicListAPIView(generics.ListAPIView):
    """Список тем"""
    queryset = ChatTopic.objects.all()
    serializer_class = serializers.TopicListSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('title', 'description')


class ChatListCreateAPIView(generics.ListCreateAPIView):
    """Создание и список чатов"""
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (ClientPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ('topic__title',)
    filterset_class = ChatListFilter
    ordering_fields = ('last_message_created_at', 'created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.ChatCreateSerializer
        return serializers.ChatListSerializer

    def get_queryset(self):
        queryset = Chat.objects.filter(
            client=self.request.user
        ).select_related(
            'topic',
        ).prefetch_related(
            Prefetch('messages', queryset=ChatMessage.objects.prefetch_related('files').order_by('-created_at'),
                     to_attr='last_messages')
        ).annotate(
            last_message_created_at=Coalesce(
                Max('messages__created_at'), 'created_at'
            ),
            unread_messages_count=Count(
                'messages',
                filter=Q(Q(messages__is_read=False) & ~Q(messages__sender_id=self.request.user.pk)),
                distinct=True
            )
        ).order_by('-last_message_created_at')
        return queryset


class ChatMessageListAPIView(generics.ListAPIView):
    """"""
    serializer_class = serializers.ChatMessageListSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (ClientPermission,)

    def get_queryset(self):
        chat_id = self.kwargs['pk']
        if not Chat.objects.filter(client=self.request.user, id=chat_id).exists():
            raise NotFound('Чат не найден')
        queryset = ChatMessage.objects.filter(
            chat_id=chat_id
        ).prefetch_related('files')
        return queryset


class ChatMessageCreateAPIView(generics.CreateAPIView):
    """Создание сообщения в чате"""
    serializer_class = serializers.ChatMessageCreateSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (ClientPermission,)

    @swagger_auto_schema(responses=swagger_docs.CREATE_CHAT_MESSAGE)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ChatMessageReadAPIView(generics.GenericAPIView):
    """Отметить сообщения в чате как прочитанные """
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (ClientPermission,)
    pagination_class = None

    # @swagger_auto_schema(
    #     manual_parameters=[
    #         openapi.Parameter('chat_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
    #         openapi.Parameter('message_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
    #     ],
    #     operation_description="Отметить сообщения в чате как прочитанные нужно отправить последний id сообщения",
    # )
    def get(self, request, *args, **kwargs):
        chat = Chat.objects.filter(client_id=self.request.user.pk, id=self.kwargs['chat_id']).first()
        if chat:
            chat.messages.filter(
                Q(id__lte=self.kwargs['message_id']) & ~Q(sender_id=self.request.user.pk)
            ).update(is_read=True)
            ws_read_chat_message(chat, self.request.user, self.kwargs['message_id'])
        return Response(status=status.HTTP_200_OK)
