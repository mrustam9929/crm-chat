from django.conf import settings
from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from apps.chat.models import Chat, ChatMessage, ChatMessageFile, ChatTopic, ChatComment
from apps.chat.utils import ChatStatus, MessageType
from apps.users.models import User
from apps.users.utils import UserRole
from ws.utils import ws_event_new_chat, ws_event_new_message, ws_update_chat_status, ws_event_update_message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'name'
        )


class CuratorChatInfoSerializer(serializers.Serializer):
    topic_count = serializers.IntegerField()
    order_count = serializers.IntegerField()


class CuratorChatTopicListSerializer(serializers.ModelSerializer):
    chat_count = serializers.IntegerField()

    class Meta:
        model = ChatTopic
        fields = (
            'id', 'title', 'logo', 'chat_count'
        )


class CuratorChatListTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatTopic
        fields = (
            'id', 'title', 'logo'
        )
        ref_name = ''


class CuratorChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'is_online', 'username'
        )


class CuratorChatMessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessageFile
        fields = (
            'id', 'file'
        )


class CuratorChatListLastMessageSerializer(serializers.ModelSerializer):
    is_my_message = serializers.SerializerMethodField()
    files = CuratorChatMessageFileSerializer(many=True)

    class Meta:
        model = ChatMessage
        fields = (
            'id', 'text', 'created_at', 'is_read', 'message_type', 'is_my_message', 'files'
        )

    def get_is_my_message(self, obj) -> bool:
        return obj.sender_id == self.context['request'].user.pk


class CuratorChatListSerializer(serializers.ModelSerializer):
    topic = CuratorChatListTopicSerializer()
    client = CuratorChatUserSerializer()
    curator = CuratorChatUserSerializer()
    last_message = CuratorChatListLastMessageSerializer()
    unread_messages_count = serializers.IntegerField()

    class Meta:
        model = Chat
        fields = (
            'id', 'client', 'curator', 'topic', 'status', 'chat_type', 'unread_messages_count',
            'last_message', 'created_at'
        )


class CuratorChatCreateSerializer(serializers.ModelSerializer):
    client = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.filter(role=UserRole.CLIENT))

    class Meta:
        model = Chat
        fields = (
            'id', 'client', 'created_at'
        )

    def create(self, validated_data):
        user = self.context['request'].user
        chat = Chat.objects.create_curator_chat(
            curator=user,
            client=validated_data['client']
        )
        ws_event_new_chat(chat, user)
        return chat


class CuratorChatUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = (
            'topic', 'status'
        )
        extra_kwargs = {
            'status': {'required': False},
            'topic': {'required': False}
        }

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if 'status' in validated_data:
            ws_update_chat_status(instance, self.context['request'].user)
        return instance


class ChatAssignCuratorSerializer(serializers.Serializer):
    curator = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.filter(role=UserRole.CURATOR))
    chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all())


class CuratorChatMessageListSerializer(serializers.ModelSerializer):
    is_my_message = serializers.SerializerMethodField()
    files = CuratorChatMessageFileSerializer(many=True)

    class Meta:
        model = ChatMessage
        fields = (
            'id', 'text', 'created_at', 'is_read', 'message_type', 'is_my_message', 'files'
        )

    def get_is_my_message(self, obj) -> bool:  # FIXME изменить если в чат могут писать несколько кураторов
        return obj.sender_id == self.context['request'].user.pk


class CuratorChatMessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = (
            'id', 'text', 'message_type'
        )

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        ws_event_update_message(self.context['request'].user, instance, self.context['request'])
        return instance


class CuratorChatMessageCreateSerializer(serializers.ModelSerializer):
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
        serializer = CuratorChatMessageListSerializer(instance, context=self.context)
        return serializer.data

    def validate_chat(self, value: Chat):
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


class CuratorChatCommentSerializer(serializers.ModelSerializer):
    curator = UserSerializer()

    class Meta:
        model = ChatComment
        fields = (
            'id', 'text', 'created_at', 'curator'
        )


class CuratorChatCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatComment
        fields = (
            'id', 'text', 'chat'
        )

    def create(self, validated_data):
        validated_data['curator'] = self.context['request'].user
        instance = super().create(validated_data)
        return instance


class CuratorChatCommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatComment
        fields = (
            'id', 'text'
        )
