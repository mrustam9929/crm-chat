from django.db import models


class ChatStatus(models.TextChoices):
    OPEN = 'open', 'Открытый'
    IN_PROGRESS = 'in_progress', 'В процессе'
    CLOSED = 'closed', 'Закрыт'
    DELAYED = 'delayed', 'Отложен'


class ChatType(models.TextChoices):
    TOPIC = 'topic', 'Тема'
    ORDER = 'order', 'Заказ'


class MessageType(models.TextChoices):
    EMOJI = 'emoji', 'Эмодзи'
    TEXT = 'text', 'Текст'
    FILE = 'file', 'Файл'
