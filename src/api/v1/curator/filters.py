from apps.chat.models import Chat
from core.generics.filters import CharInFilter
from django.db.models import Q
from django_filters import rest_framework as filters

CHAT_FILTER = (
    'my',  # Мои чаты
    'others',  # Чужие чаты
    'not_curator',  # Не назначенные кураторы
)


class ChatListFilter(filters.FilterSet):
    chats = CharInFilter(method='filter_chats')

    class Meta:
        model = Chat
        fields = (
            'topic', 'chat_type', 'status', 'chats'
        )

    def filter_chats(self, queryset, field_name, value):
        q = Q()
        if 'my' in value:
            q |= Q(curator_id=self.request.user.id)
        if 'others' in value:
            q |= Q(~Q(curator_id=self.request.user.id) & Q(curator_id__isnull=False))
        if 'not_curator' in value:
            q |= Q(curator_id__isnull=True)
        print(q)
        return queryset.filter(q)
