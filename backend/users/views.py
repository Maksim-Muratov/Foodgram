from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
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

    @action(
        methods=[
            'get',
        ],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(subscribed__user=user)
        pages = self.paginate_queryset(subscriptions)
        serializer = SubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author,
                data=request.data,
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = get_object_or_404(Subscribe, user=user, author=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return User.objects.all()
