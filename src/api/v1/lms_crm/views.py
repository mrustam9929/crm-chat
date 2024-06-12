import datetime

from django.db.models import Q, Count, Avg, F, Prefetch
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, permissions
from rest_framework.response import Response

from api.v1.authentication import KeyCloakAuthentication
from api.v1.lms_crm import serializers
from api.v1.lms_crm.utils import get_filter_date
from apps.chat.models import ChatMessage, ChatTopic, Chat
from apps.chat.utils import ChatType, ChatStatus
from apps.users.models import User
from apps.users.utils import UserRole


class UserNotificationAPIView(generics.GenericAPIView):
    """Уведомления пользователя"""
    serializer_class = serializers.UserNotificationSerializer
    pagination_class = None
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.role == UserRole.CURATOR:
            q = Q(chat__curator_id=user.pk)
        else:
            q = Q(chat__client_id=user.pk)
        has_notifications = ChatMessage.objects.filter(
            Q(is_read=False) & ~Q(sender_id=self.request.user.pk) & q
        ).exists()
        return Response(data={'has_notifications': has_notifications}, status=status.HTTP_200_OK)


class TopicsPopularityAPIView(generics.ListAPIView):
    """Наиболее популярные темы"""
    serializer_class = serializers.TopicsPopularitySerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        has_date_filter, start_date, end_date = get_filter_date(self.request.query_params)
        if has_date_filter:
            q = Q(chats__created_at__gte=start_date, chats__created_at__lte=end_date)
        else:
            q = Q()
        return ChatTopic.objects.all().annotate(
            chats_count=Count('chats', filter=q)
        ).order_by(
            '-chats_count'
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['all_chats_count'] = Chat.objects.all().count()
        return context

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ChatsAvgResolutionTimeAPIView(generics.GenericAPIView):
    """Среднее время разрешения тем"""
    serializer_class = serializers.ChatsAvgResolutionTimeSerializer
    pagination_class = None
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, *args, **kwargs):
        has_date_filter, start_date, end_date = get_filter_date(self.request.query_params)
        if has_date_filter:
            q = Q(created_at__gte=start_date, created_at__lte=end_date)
        else:
            q = Q()
        avg_time = Chat.objects.filter(
            Q(chat_type=ChatType.TOPIC, status=ChatStatus.CLOSED) & q
        ).aggregate(
            avg_time=Avg(F('closed_at') - F('created_at')),
        )['avg_time']
        avg_time = avg_time or datetime.timedelta(seconds=0)

        return Response(data={'avg_time': avg_time.seconds}, status=status.HTTP_200_OK)


class TopicsAvgResolutionTimeAPIView(generics.ListAPIView):
    """Время разрешения по темам"""
    serializer_class = serializers.TopicsAvgResolutionTimeSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        has_date_filter, start_date, end_date = get_filter_date(self.request.query_params)
        q = Q(chat_type=ChatType.TOPIC, status=ChatStatus.CLOSED)
        if has_date_filter:
            q &= Q(created_at__gte=start_date, created_at__lte=end_date)

        return ChatTopic.objects.all().prefetch_related(
            Prefetch(
                'chats',
                queryset=Chat.objects.filter(q).annotate(
                    avg_time=Avg(F('closed_at') - F('created_at'))
                ),
                to_attr='chats_avg_time'
            )
        )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ClosedChatPercentageAPIView(generics.GenericAPIView):
    """Процент решенных тикетов"""
    serializer_class = serializers.ClosedChatPercentageSerializer
    pagination_class = None
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, *args, **kwargs):
        has_date_filter, start_date, end_date = get_filter_date(self.request.query_params)
        if has_date_filter:
            q = Q(created_at__gte=start_date, created_at__lte=end_date)
        else:
            q = Q()
        chats = Chat.objects.filter(q).aggregate(
            all_chats_count=Count('id'),
            closed_chats_count=Count('id', filter=Q(status=ChatStatus.CLOSED))
        )
        if chats['all_chats_count'] == 0:
            closed_chat_percentage = 0.0
        else:
            closed_chat_percentage = chats['closed_chats_count'] / chats['all_chats_count'] * 100.0

        return Response(data={'closed_chat_percentage': closed_chat_percentage}, status=status.HTTP_200_OK)


class ClosedChatPercentageForTopicAPIView(generics.ListAPIView):
    """Процент решенных тикетов по каждой теме"""
    serializer_class = serializers.ClosedChatPercentageForTopicSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        has_date_filter, start_date, end_date = get_filter_date(self.request.query_params)
        if has_date_filter:
            q = Q(created_at__gte=start_date, created_at__lte=end_date)
        else:
            q = Q()
        return ChatTopic.objects.all().annotate(
            all_chats_count=Count('chats', filter=q),
            closed_chats_count=Count('chats', filter=Q(chats__status=ChatStatus.CLOSED) & q)
        )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CuratorChatsAPIView(generics.ListAPIView):
    """ Количество тикетов по менеджерам"""
    serializer_class = serializers.CuratorChatsSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        has_date_filter, start_date, end_date = get_filter_date(self.request.query_params)
        q = Q(curator_chats__status=ChatStatus.CLOSED)
        if has_date_filter:
            q &= Q(curator_chats__closed_at__gte=start_date, curator_chats__closed_at__lte=end_date)

        return User.objects.filter(role=UserRole.CURATOR).annotate(
            chat_count=Count('curator_chats', filter=q)
        )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CuratorChatsAvgTimeAPIView(generics.ListAPIView):
    """ Cреднее время разрешения тикетов для каждого менеджера."""
    serializer_class = serializers.CuratorChatsAvgTimeSerializer
    authentication_classes = (KeyCloakAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        has_date_filter, start_date, end_date = get_filter_date(self.request.query_params)
        q = Q(status=ChatStatus.CLOSED)
        if has_date_filter:
            q &= Q(closed_at__gte=start_date, closed_at__lte=end_date)

        return User.objects.filter(role=UserRole.CURATOR).prefetch_related(
            Prefetch(
                'curator_chats',
                queryset=Chat.objects.filter(
                    Q(chat_type=ChatType.TOPIC, status=ChatStatus.CLOSED) & q
                ).annotate(
                    resolution_time=F('closed_at') - F('created_at')
                ),
                to_attr='chats_avg_time'
            )
        )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
