from rest_framework.permissions import BasePermission, SAFE_METHODS


class RecipePermission(BasePermission):
    """
    Права доступа для вьюсета рецептов:
    - Обновление/удаление - автор или админ
    - Создание - аутентифицированные пользователи
    - Безопасные методы - все пользователи
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or (request.user.is_authenticated and obj.author == request.user)
        )
