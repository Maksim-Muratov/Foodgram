from django.contrib import admin

from .models import Ingredient, Tag


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
