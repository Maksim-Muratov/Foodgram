from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group


User = get_user_model()

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(UserAdmin):
    """Конфиг админ-зоны для модели пользователя."""

    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
    )
    search_fields = ('username', 'email',)
    list_filter = ('is_staff',)
    list_display_links = ('username', 'email',)
