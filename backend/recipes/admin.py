from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class RecipeIngredientInline(admin.StackedInline):
    """Конфиг для отображения ингредиентов на странице рецепта."""

    model = IngredientInRecipe
    extra = 0


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Конфиг админ-зоны для модели ингредиента."""

    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    list_display_links = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Конфиг админ-зоны для модели тега."""

    list_display = (
        'name',
        'color',
        'slug'
    )
    search_fields = ('name',)
    list_display_links = ('name', 'slug',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Конфиг админ-зоны для модели рецепта."""

    list_display = (
        'name',
        'author',
        'added_to_favorite'
    )
    search_fields = ('name', 'author',)
    list_filter = ('author', 'tags',)
    list_display_links = ('name',)
    inlines = (RecipeIngredientInline, )

    @admin.display(description='Добавлен в избранное')
    def added_to_favorite(self, obj):
        return f'{obj.favorites.count()}'


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Конфиг админ-зоны для модели ингредиента в рецепте."""

    list_display = (
        'id',
        'ingredient',
        'recipe',
        'amount'
    )
    search_fields = ('recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Конфиг админ-зоны для модели избранного."""

    list_display = (
        'id',
        'user',
        'recipe'
    )
    list_filter = ('recipe',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Конфиг админ-зоны для модели корзины."""

    list_display = (
        'id',
        'user',
        'recipe'
    )
    search_fields = ('user',)
