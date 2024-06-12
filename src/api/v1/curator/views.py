from django.db.models import Max, Prefetch, Q, Count
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from api.v1.authentication import KeyCloakAuthentication
from api.v1.curator import serializers
from api.v1.curator import swagger_docs
from api.v1.curator.filters import ChatListFilter
from api.v1.permissions import CuratorPermission
from apps.chat.models import ChatTopic, Chat, ChatMessage, ChatComment
from apps.chat.utils import ChatType
from core.libs.keycloak import get_keycloak_user_roles
from ws.utils import ws_event_assign_curator, ws_update_chat_status, ws_read_chat_message, ws_event_delete_message


class ChatInfoAPIView(generics.RetrieveAPIView):
    """
    Информация о чате количество обращений и заказов
    """
    serializer_class = serializers.CuratorChatInfoSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (CuratorPermission,)

    def get_object(self):
        chats_count = Chat.objects.filter(
            topic__permission__in=get_keycloak_user_roles(self.request.META.get('HTTP_AUTHORIZATION'))
        ).aggregate(
            topic_count=Count('id', filter=Q(chat_type=ChatType.TOPIC)),
            order_count=Count('id', filter=Q(chat_type=ChatType.ORDER)),
        )
        return chats_count


class ChatTopicListAPIView(generics.ListAPIView):
    """
    Список тем чатов
    """
    serializer_class = serializers.CuratorChatTopicListSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (CuratorPermission,)

    def get_queryset(self):
        queryset = ChatTopic.objects.filter(
            permission__in=get_keycloak_user_roles(self.request.META.get('HTTP_AUTHORIZATION'))
        ).annotate(
            chat_count=Count('chats')
        )
        return queryset


class ChatCreateListAPIView(generics.ListCreateAPIView):
    """
    Список чатов и создание заказа
    """
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ('client__name',)
    filterset_class = ChatListFilter
    ordering_fields = ('last_message_created_at', 'created_at')
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (CuratorPermission,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CuratorChatCreateSerializer
        return serializers.CuratorChatListSerializer

    def get_queryset(self):
        queryset = Chat.objects.filter(
            topic__permission__in=get_keycloak_user_roles(self.request.META.get('HTTP_AUTHORIZATION'))
        ).select_related(
            'topic', 'client', 'curator'
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


class ChatMessageReadAPIView(generics.GenericAPIView):
    """Отметить сообщения в чате как прочитанные """
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (CuratorPermission,)
    pagination_class = None

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('chat_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('message_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
        ],
        operation_description="Отметить сообщения в чате как прочитанные нужно отправить последний id сообщения",
    )
    def get(self, request, *args, **kwargs):
        chat = Chat.objects.filter(id=self.kwargs['chat_id']).first()
        if chat:
            ChatMessage.objects.filter(
                Q(chat_id=self.kwargs['chat_id']) &
                Q(id__lte=self.kwargs['message_id']) &
                ~Q(sender_id=self.request.user.pk)

            ).update(is_read=True)
            ws_read_chat_message(chat, self.request.user, self.kwargs['message_id'])
        return Response(status=status.HTTP_200_OK)


class ChatCommentCreateAPIView(generics.CreateAPIView):
    """Создание и список комментариев к чату"""
    serializer_class = serializers.CuratorChatCommentCreateSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (CuratorPermission,)


class ChatCommentListAPIView(generics.ListAPIView):
    """Создание и список комментариев к чату"""
    serializer_class = serializers.CuratorChatCommentSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (CuratorPermission,)

    def get_queryset(self):
        return ChatComment.objects.filter(
            chat_id=self.kwargs['pk']
        ).select_related('curator')


class ChatCommentUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Редактирование и удаление комментария к чату"""
    serializer_class = serializers.CuratorChatCommentUpdateSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (CuratorPermission,)
    http_method_names = ('patch', 'delete')

    def get_queryset(self):
        return ChatComment.objects.filter(curator=self.request.user)


class ChatCloseAPIView(generics.GenericAPIView):
    """Закрытие чата"""
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (CuratorPermission,)
    http_method_names = ('get',)
    pagination_class = None

    def get(self, request, *args, **kwargs):
        chat = self.get_object()
        chat.close_chat()
        ws_update_chat_status(chat, self.request.user)
        return Response(status=status.HTTP_200_OK)

    def get_queryset(self):
        return Chat.objects.all()


class ChatUpdateAPIView(generics.UpdateAPIView):
    """Редактирование темы чата"""
    serializer_class = serializers.CuratorChatUpdateSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (CuratorPermission,)
    http_method_names = ('put',)

    def get_queryset(self):
        return Chat.objects.filter(
            topic__permission__in=get_keycloak_user_roles(self.request.META.get('HTTP_AUTHORIZATION'))
        )


class ChatAssignCuratorAPIView(generics.GenericAPIView):
    """Назначить куратора"""
    serializer_class = serializers.ChatAssignCuratorSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (CuratorPermission,)
    http_method_names = ('post',)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat: Chat = serializer.validated_data['chat']
        chat.assign_curator(serializer.validated_data['curator'])
        ws_event_assign_curator(chat, self.request.user)
        return Response(status=status.HTTP_200_OK)


class ChatMessageListAPIView(generics.ListAPIView):
    """Сообщения в чата"""
    serializer_class = serializers.CuratorChatMessageListSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (CuratorPermission,)

    def get_queryset(self):
        queryset = ChatMessage.objects.filter(
            chat_id=self.kwargs['pk']
        ).prefetch_related('files')
        return queryset


class ChatMessageUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Редактирование и удаление сообщения в чате"""
    serializer_class = serializers.CuratorChatMessageUpdateSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (CuratorPermission,)
    http_method_names = ('put', 'delete')

    def get_queryset(self):
        return ChatMessage.objects.all()

    def perform_destroy(self, instance):
        chat = instance.chat
        message_id = instance.id
        instance.delete()
        ws_event_delete_message(self.request.user, chat, message_id, chat.client_id)


class ChatMessageCreateAPIView(generics.CreateAPIView):
    """Создание сообщения в чате"""
    serializer_class = serializers.CuratorChatMessageCreateSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (CuratorPermission,)

    @swagger_auto_schema(responses=swagger_docs.CREATE_CHAT_MESSAGE)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
