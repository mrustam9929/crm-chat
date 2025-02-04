# Generated by Django 5.0.2 on 2024-05-21 14:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_chat_closed_at'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chat',
            name='closed_at',
        ),
        migrations.RemoveField(
            model_name='chat',
            name='curator_note',
        ),
        migrations.CreateModel(
            name='ChatComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('text', models.TextField(max_length=10000, verbose_name='Текст')),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='chat.chat', verbose_name='Чат')),
                ('curator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_comments', to=settings.AUTH_USER_MODEL, verbose_name='Куратор')),
            ],
            options={
                'verbose_name': 'Комментарий к чату',
                'verbose_name_plural': 'Комментарии к чатам',
                'db_table': 'chat_comments',
            },
        ),
    ]
