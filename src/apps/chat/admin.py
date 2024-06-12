from django.contrib import admin

from apps.chat.models import ChatTopic


@admin.register(ChatTopic)
class ChatTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
