from django.contrib.auth import get_user_model
from djoser.views import UserViewSet

from api.v1.serializers import CustomUserSerializer
from .pagination import CustomPageNumberPagination


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Переопределение базового вьюсета Djoser"""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return User.objects.all()
