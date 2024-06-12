from rest_framework import serializers

from apps.chat.models import ChatMessage, ChatMessageFile


class WsChatMessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessageFile
        fields = (
            'id', 'file'
        )


class WsChatMessageEventSerializer(serializers.ModelSerializer):
    files = WsChatMessageFileSerializer(many=True)
    chat_id = serializers.IntegerField(source='chat.id')

    class Meta:
        model = ChatMessage
        fields = (
            'id', 'chat_id', 'sender', 'text', 'message_type', 'is_read', 'created_at', 'files'
        )
