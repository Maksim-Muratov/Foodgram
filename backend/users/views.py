from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.serializers import CustomUserSerializer, SubscribeSerializer

from .models import Subscribe
from .pagination import CustomPageNumberPagination


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Переопределение базового вьюсета пользователя (Djoser)."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPageNumberPagination

    def get_permissions(self):
        """Устанавливаем права доступа для отдельных запросов."""
        if self.action in [
            'me', 'subscribe', 'delete_subscribe', 'subscriptions'
        ]:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        """Подписки."""
        subscriptions = User.objects.filter(author__user=request.user)
        pages = self.paginate_queryset(subscriptions)
        serializer = SubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post'], detail=True)
    def subscribe(self, request, **kwargs):
        """Подписаться."""
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        serializer = SubscribeSerializer(
            author,
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        Subscribe.objects.create(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        """Отписаться."""
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        get_object_or_404(Subscribe, user=request.user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
