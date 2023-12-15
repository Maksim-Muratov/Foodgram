from django.contrib.auth import get_user_model
from django_filters.rest_framework import (
    FilterSet,
    ModelMultipleChoiceFilter,
    filters,
)

from recipes.models import Recipe, Tag, Favorite, ShoppingCart

User = get_user_model()


class RecipeFilter(FilterSet):
    """Фильтр для вьюсета рецептов"""

    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        label='Tags'
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def filter_is_favorited(self, queryset, name, value):
        """Фильтр по избранному"""
        if value:
            favorites = Favorite.objects.filter(
                user=self.request.user.id).values_list('recipe_id', flat=True)
            return queryset.filter(id__in=favorites)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр по корзине покупок"""
        if value:
            shopping_carts = ShoppingCart.objects.filter(
                user=self.request.user.id).values_list('recipe_id', flat=True)
            return queryset.filter(id__in=shopping_carts)
        return queryset
