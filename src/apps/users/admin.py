from django.contrib import admin
from apps.users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'role')
    search_fields = ('username', 'name')
    list_filter = ('role',)
    ordering = ('username', 'name')
    readonly_fields = ('username',)
    fields = ('username', 'name', 'role')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
