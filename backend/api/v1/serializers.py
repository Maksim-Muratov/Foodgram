import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag,
    Favorite,
    ShoppingCart
)
from users.models import Subscribe


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Переопределение базового сериализатора пользователя (Djoser)."""

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
        return (user.is_authenticated
                and user.subscriber.filter(author=author).exists())


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Переопределение базового сериализатора создания пользователя (Djoser).
    """

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


class Base64ImageField(serializers.ImageField):
    """Сериализатор изображения."""

    def to_internal_value(self, data):
        """Преобразование base64 строки в файл изображения"""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Краткий сериализатор рецепта."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscribeSerializer(CustomUserSerializer):
    """Сериализатор подписки."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = (
            *CustomUserSerializer.Meta.fields,
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )

    def validate(self, data):
        """Валидация."""
        author = self.instance
        user = self.context['request'].user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError({
                'errors': 'Вы уже подписаны на этого пользователя'
            })
        if user == author:
            raise ValidationError({
                'errors': 'Вы не можете подписаться на самого себя'
            })
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True, read_only=True).data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class AmountIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор количества ингредиентов."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор чтения рецепта."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = IngredientInRecipe.objects.filter(recipe=obj)
        return AmountIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated
                and user.favorites.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated
                and user.cart.filter(recipe=obj).exists())


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов в рецепте."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class WriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания, обновления и удаления рецепта."""

    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, value):
        """Валидация ингредиентов."""
        ingredients = value
        if not ingredients:
            raise ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент'
            })
        ingredients_list = []
        for item in ingredients:
            try:
                ingredient = Ingredient.objects.get(id=item['id'])
            except Exception:
                raise ValidationError({
                    'ingredients': 'Такого ингредиента нет в базе данных'
                })
            if ingredient in ingredients_list:
                raise ValidationError({
                    'ingredients': 'Ингридиенты не могут повторяться'
                })
            if int(item['amount']) <= 0:
                raise ValidationError({
                    'amount': 'Количество ингредиента должно быть больше 0'
                })
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        """Валидация тегов."""
        tags = value
        if not tags:
            raise ValidationError({'tags': 'Нужно выбрать хотя бы один тег'})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({'tags': 'Теги не должны повторяться'})
            tags_list.append(tag)
        return value

    def create_ingredients(self, ingredients, recipe):
        """Присваивание ингредиентов рецепту."""
        IngredientInRecipe.objects.bulk_create(
            IngredientInRecipe(
                ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        )

    def create(self, validated_data):
        """Создание."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Обновление."""
        try:
            tags = validated_data.pop('tags')
        except Exception:
            raise ValidationError({
                'tags': 'Нужно выбрать хотя бы один тег'
            })
        try:
            ingredients = validated_data.pop('ingredients')
        except Exception:
            raise ValidationError({
                'ingredients': 'Нужно выбрать хотя бы один ингредиент'
            })
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.ingredients.clear()
        instance.tags.set(tags)
        self.create_ingredients(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context['request']
        context = {'request': request}
        return ReadRecipeSerializer(instance, context=context).data


class AbstractSerializer(serializers.ModelSerializer):
    """Абстрактный сериализатор для корзины и избранного."""

    class Meta:
        abstract = True

    def validate(self, data):
        """Валидация повторного добавления."""
        user = data.get('user')
        recipe = data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError({'error': 'Рецепт уже добавлен.'})
        return data


class ShoppingCartSerializer(AbstractSerializer):
    """Сериализатор корзины."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')


class FavoriteSerializer(AbstractSerializer):
    """Сериализатор избранного."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
