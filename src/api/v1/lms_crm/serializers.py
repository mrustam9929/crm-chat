from rest_framework import serializers

from apps.chat.models import ChatTopic
from apps.users.models import User


class UserNotificationSerializer(serializers.Serializer):
    has_notifications = serializers.BooleanField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class TopicsPopularitySerializer(serializers.ModelSerializer):
    popularity = serializers.SerializerMethodField()

    class Meta:
        model = ChatTopic
        fields = (
            'id', 'title', 'description', 'logo', 'popularity'
        )

    def get_popularity(self, obj) -> float:
        return (obj.chats_count / self.context['all_chats_count']) * 100.0


class ChatsAvgResolutionTimeSerializer(serializers.Serializer):
    avg_time = serializers.CharField()


class TopicsAvgResolutionTimeSerializer(serializers.ModelSerializer):
    avg_time = serializers.SerializerMethodField()

    class Meta:
        model = ChatTopic
        fields = (
            'id', 'title', 'description', 'logo', 'avg_time'
        )

    def get_avg_time(self, obj) -> float:
        chats = obj.chats_avg_time
        chats_count = len(chats)
        if chats_count == 0:
            return 0
        return sum([c.avg_time.seconds for c in chats]) / len(chats)


class ClosedChatPercentageForTopicSerializer(serializers.ModelSerializer):
    closed_chat_percent = serializers.SerializerMethodField()

    class Meta:
        model = ChatTopic
        fields = (
            'id', 'title', 'description', 'logo', 'closed_chat_percent'
        )

    def get_closed_chat_percent(self, obj) -> float:
        if obj.all_chats_count == 0:
            return 0.0
        return (obj.closed_chats_count / obj.all_chats_count) * 100.0


class ClosedChatPercentageSerializer(serializers.Serializer):
    closed_chat_percentage = serializers.FloatField()


class CuratorChatsSerializer(serializers.ModelSerializer):
    chat_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'name', 'chat_count'
        )


class CuratorChatsAvgTimeSerializer(serializers.ModelSerializer):
    avg_time = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'name', 'avg_time'
        )

    def get_avg_time(self, obj):
        chats = obj.chats_avg_time
        if not chats:
            return 0
        return sum(c.resolution_time.seconds for c in chats) / len(chats)
