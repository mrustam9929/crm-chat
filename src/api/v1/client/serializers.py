from django.conf import settings
from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from apps.chat.models import Chat, ChatMessage, ChatMessageFile, ChatTopic
from apps.chat.utils import ChatStatus, MessageType
from ws.utils import ws_event_new_chat, ws_event_new_message


class TopicListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatTopic
        fields = (
            'id', 'title', 'description', 'logo'
        )


class ChatCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = (
            'id', 'topic', 'created_at', 'status', 'chat_type'
        )
        read_only_fields = ('id', 'created_at', 'status', 'chat_type')

    def create(self, validated_data):
        user = self.context['request'].user
        chat = Chat.objects.create_client_chat(
            client=user,
            topic=validated_data['topic']
        )
        ws_event_new_chat(chat, user)
        return chat


class ChatTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatTopic
        fields = (
            'id', 'title', 'logo'
        )


class ChatMessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessageFile
        fields = (
            'id', 'file'
        )


class ChatListLastMessageSerializer(serializers.ModelSerializer):
    is_my_message = serializers.SerializerMethodField()
    files = ChatMessageFileSerializer(many=True)

    class Meta:
        model = ChatMessage
        fields = (
            'id', 'text', 'created_at', 'is_read', 'message_type', 'is_my_message', 'files'
        )

    def get_is_my_message(self, obj) -> bool:
        return obj.sender_id == self.context['request'].user.pk


class ChatListSerializer(serializers.ModelSerializer):
    topic = ChatTopicSerializer()
    last_message = ChatListLastMessageSerializer()
    unread_messages_count = serializers.IntegerField()

    class Meta:
        model = Chat
        fields = (
            'id', 'topic', 'created_at', 'status', 'chat_type', 'last_message', 'unread_messages_count'
        )


class ChatMessageListSerializer(serializers.ModelSerializer):
    is_my_message = serializers.SerializerMethodField()
    files = ChatMessageFileSerializer(many=True)

    class Meta:
        model = ChatMessage
        fields = (
            'id', 'text', 'created_at', 'is_read', 'message_type', 'is_my_message', 'files'
        )

    def get_is_my_message(self, obj) -> bool:
        return obj.sender_id == self.context['request'].user.pk


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    files = serializers.ListField(
        child=serializers.FileField(validators=[FileExtensionValidator(settings.CHAT_MESSAGE_ALLOWED_FILE_EXTENSIONS)]),
        write_only=True,
        required=False
    )

    class Meta:
        model = ChatMessage
        fields = (
            'id', 'text', 'message_type', 'files', 'chat'
        )

    def create(self, validated_data):
        user = self.context['request'].user
        files = validated_data.pop('files', [])
        message = ChatMessage.objects.create(
            sender=user,
            **validated_data
        )
        for file in files:
            ChatMessageFile.objects.create(
                message=message,
                file=file
            )
        ws_event_new_message(message, user, self.context['request'])
        return message

    def to_representation(self, instance):
        serializer = ChatMessageListSerializer(instance, context=self.context)
        return serializer.data

    def validate_chat(self, value: Chat):
        if value.client_id != self.context['request'].user.pk:
            raise serializers.ValidationError('Чат не найден')
        if value.status == ChatStatus.CLOSED:
            raise serializers.ValidationError('Чат закрыт')
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['message_type'] == MessageType.TEXT and not attrs.get('text'):
            raise serializers.ValidationError({'message_type': 'поле text не должно быть пустым'})
        if attrs['message_type'] == MessageType.FILE and not attrs.get('files'):
            raise serializers.ValidationError({'message_type': 'поле files не должно быть пустым'})
        return attrs

    def validate_files(self, value):
        if value and max(map(lambda x: x.size, value)) > settings.CHAT_MESSAGE_FILE_MAX_SIZE * 1024 * 1024:
            raise serializers.ValidationError(f'Максимальный размер файла {settings.CHAT_MESSAGE_FILE_MAX_SIZE} MB')
        return value
