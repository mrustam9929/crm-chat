import pdb
from django_filters import rest_framework as filters

from apps.chat.models import Chat


class ChatListFilter(filters.FilterSet):
    class Meta:
        model = Chat
        fields = (
            'topic',
        )
