from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Tag


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, author):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return user.subscriber.filter(author=author).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    password = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class SubscribeSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = (
            *CustomUserSerializer.Meta.fields,
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes(self, obj):
        ...

    def get_recipes_count(self, obj):
        ...


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
