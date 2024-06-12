import random
from datetime import timedelta

from django.core.management.base import BaseCommand

from apps.chat.models import Chat, ChatTopic
from apps.users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        Chat.objects.all().delete()
        client = User.objects.get(id=99)
        curator = User.objects.get(id=55)
        topics = ChatTopic.objects.all()

        for _ in range(1000):
            chat = Chat.objects.create(
                client=client,
                curator=curator,
                topic=random.choice(topics),
                status='closed',
                chat_type='topic',
            )
            Chat.objects.create(
                client=client,
                curator=curator,
                topic=random.choice(topics),
                status='open',
                chat_type='topic',
            )
            chat.closed_at = chat.created_at + timedelta(seconds=random.randint(1, 100))
            chat.save()
