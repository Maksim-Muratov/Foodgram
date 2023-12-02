from rest_framework.permissions import BasePermission


SAFE_METHODS = ('GET', 'POST', 'OPTIONS', 'HEAD')


class CustomUserPermission(BasePermission):
    """Кастомный permission для работы с пользователями."""

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user or request.user.is_superuser
