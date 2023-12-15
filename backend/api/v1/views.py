from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.pagination import CustomPageNumberPagination

from .filters import RecipeFilter
from .permissions import RecipePermission
from .serializers import (
    IngredientSerializer,
    ReadRecipeSerializer,
    TagSerializer,
    WriteRecipeSerializer,
    ShoppingCartSerializer,
    FavoriteSerializer,
    ShortRecipeSerializer
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""

    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        """Позволяет искать ингредиенты по параметру name"""
        if self.request.query_params and 'name' in self.request.query_params:
            search_value = self.request.query_params['name']
            return Ingredient.objects.filter(
                name__icontains=search_value,
            )
        return Ingredient.objects.all()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.all()
    pagination_class = CustomPageNumberPagination
    permission_classes = [RecipePermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        """Сохраняем автора рецепта."""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Сохраняем автора рецепта."""
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """В зависимости от запроса возвращаем Read или Write сериализатор"""
        if self.action in ('retrieve', 'list'):
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачать корзину."""
        user = request.user
        ingredients = (
            IngredientInRecipe.objects.filter(recipe__cart__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .order_by('ingredient__name')
            .annotate(amount=Sum('amount'))
        )
        shopping_cart = 'Для выбранных рецептов вам понадобится:\n\n'
        shopping_cart += '\n'.join(
            [
                f'{ingredient["ingredient__name"]}'
                f' — {ingredient["amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}'
                for ingredient in ingredients
            ]
        )
        response = HttpResponse(
            shopping_cart, content_type='text.txt; charset=utf-8'
        )
        file_name = f'{user.username}_shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Добавить в корзину."""
        return self.add_recipe(ShoppingCartSerializer, request, pk)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk):
        """Удалить из корзины."""
        return self.delete_recipe(ShoppingCart, request, pk)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Добавить в избранное."""
        return self.add_recipe(FavoriteSerializer, request, pk)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk):
        """Удалить из избранного."""
        return self.delete_recipe(Favorite, request, pk)

    def add_recipe(self, serializer, request, pk):
        """Функция добавления в корзину/избранное."""
        data = {
            'user': request.user.pk,
            'recipe': pk,
        }
        serializer = serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe_serializer = ShortRecipeSerializer(recipe)
        return Response(recipe_serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, request, pk):
        """Функция удаления из корзины/избранного."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        get_object_or_404(model, user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
