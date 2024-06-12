from typing import Optional

from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

from apps.chat.utils import ChatStatus, ChatType, MessageType
from apps.users.models import User
from core.generics.models import ModelWithDate


class ChatTopic(ModelWithDate):
    title = models.CharField(
        max_length=255, verbose_name='Название'
    )
    description = CKEditor5Field(
        max_length=10000, verbose_name='Описание',
    )
    logo = models.FileField(
        upload_to='chat_topics/logos/', verbose_name='Логотип'
    )
    permission = models.CharField(
        max_length=255, verbose_name='Права доступа к теме'
    )

    class Meta:
        db_table = 'chat_topics'
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'

    def __str__(self):
        return self.title


class ChatManager(models.Manager):

    def create_client_chat(self, client: User, topic: ChatTopic) -> 'Chat':
        """Создание чата для клиента
        :param client: User - пользователь с ролью клиента
        :param topic: ChatTopic - тема чата
        :return: Chat - созданный чат
        """
        return self.create(
            client=client,
            topic=topic,
            chat_type=ChatType.TOPIC,
            status=ChatStatus.OPEN
        )

    def create_curator_chat(self, curator: User, client: User) -> 'Chat':
        """Создание чата для куратора
        :param curator: User - куратор
        :param client: User - клиент
        :return: Chat - созданный чат
        """
        return self.create(
            curator=curator,
            client=client,
            chat_type=ChatType.ORDER,
            status=ChatStatus.OPEN
        )


class Chat(ModelWithDate):
    client = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Клиент', related_name='client_chats'
    )
    curator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name='Куратор', related_name='curator_chats'
    )
    topic = models.ForeignKey(
        ChatTopic, on_delete=models.CASCADE, verbose_name='Тема', related_name='chats', null=True
    )
    status = models.CharField(
        max_length=25, choices=ChatStatus, default=ChatStatus.OPEN, verbose_name='Статус'
    )
    chat_type = models.CharField(
        max_length=25, choices=ChatType, verbose_name='Тип чата'
    )

    objects = ChatManager()

    class Meta:
        db_table = 'chats'
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

    @property
    def last_message(self) -> Optional['ChatMessage']:
        if hasattr(self, 'last_messages'):
            if self.last_messages:
                return self.last_messages[0]
            return None
        return self.messages.first()

    def close_chat(self) -> None:
        """Закрытие чата"""
        self.status = ChatStatus.CLOSED
        self.save(update_fields=('status',))

    def assign_curator(self, curator: User) -> None:
        """Назначение куратора
        :param curator: User - куратор
        :return: None
        """
        self.curator = curator
        self.status = ChatStatus.IN_PROGRESS
        self.save(update_fields=('curator', 'status'))


class ChatComment(ModelWithDate):
    curator = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Куратор', related_name='chat_comments'
    )
    chat = models.ForeignKey(
        Chat, on_delete=models.CASCADE, verbose_name='Чат', related_name='comments'
    )
    text = models.TextField(
        max_length=10000, verbose_name='Текст'
    )

    class Meta:
        db_table = 'chat_comments'
        verbose_name = 'Комментарий к чату'
        verbose_name_plural = 'Комментарии к чатам'


class ChatMessage(ModelWithDate):
    chat = models.ForeignKey(
        Chat, on_delete=models.CASCADE, verbose_name='Чат', related_name='messages'
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Отправитель', related_name='+'
    )
    text = models.TextField(
        max_length=10000, verbose_name='Текст', null=True
    )
    message_type = models.CharField(
        max_length=25, choices=MessageType, verbose_name='Тип сообщения'
    )
    is_read = models.BooleanField(
        default=False, verbose_name='Прочитано'
    )

    class Meta:
        db_table = 'chat_messages'
        verbose_name = 'Сообщение чата'
        verbose_name_plural = 'Сообщения чатов'
        ordering = ('-created_at',)


class ChatMessageFile(ModelWithDate):
    def _get_file_path(self, filename):
        return f'Chat/{self.message.chat_id}/{filename}'

    message = models.ForeignKey(
        ChatMessage, on_delete=models.CASCADE, verbose_name='Сообщение', related_name='files'
    )
    file = models.FileField(
        upload_to=_get_file_path, verbose_name='Файл'
    )

    class Meta:
        db_table = 'chat_message_files'
        verbose_name = 'Файл сообщения'
        verbose_name_plural = 'Файлы сообщений'
