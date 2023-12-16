from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (
    INGREDIENT_NAME_LEN,
    INGREDIENT_MEASUREMENT_UNIT_LEN,
    TAG_NAME_LEN,
    TAG_SLUG_LEN,
    RECIPE_NAME_LEN,
    MIN_COOKING_TIME,
    MIN_AMOUNT
)

from .validators import HexColorValidator


User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        'Название',
        max_length=INGREDIENT_NAME_LEN
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=INGREDIENT_MEASUREMENT_UNIT_LEN
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit',
            ),
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        'Название',
        max_length=TAG_NAME_LEN,
        unique=True
    )
    slug = models.SlugField(
        'Slug',
        max_length=TAG_SLUG_LEN,
        unique=True
    )
    color = models.CharField(
        'HEX-цвет',
        max_length=7,
        unique=True,
        validators=[HexColorValidator()]
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    name = models.CharField(
        'Название',
        max_length=RECIPE_NAME_LEN,
        db_index=True,
        help_text=f'Обязательное поле. До {RECIPE_NAME_LEN} символов.'
    )
    image = models.ImageField(
        'Изображение блюда',
        upload_to='recipes/images/',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты',
        through='IngredientInRecipe'
    )
    text = models.TextField(
        'Описание',
        help_text='Обязательное поле.'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        help_text=f'Обязательное поле. Минимум {MIN_COOKING_TIME} минут.',
        validators=[
            MinValueValidator(
                limit_value=MIN_COOKING_TIME,
                message=('Минимальное время приготовления — '
                         f'{MIN_COOKING_TIME} минут.')
            )
        ]
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Модель ингридиента в рецепте."""

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиенты',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredient_list',
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                limit_value=MIN_AMOUNT,
                message=f'Минимальное количество — {MIN_AMOUNT}.'
            )
        ]
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredients_recipe'
            )
        ]

    def __str__(self):
        return f'"{self.recipe}": {self.ingredient} — {self.amount}'


class UserRecipe(models.Model):
    """Абстрактный класс для избранного и корзины."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        unique_together = ('user', 'recipe')

    def __str__(self):
        return (f'{self.user.username} добавил рецепт "{self.recipe}".')


class Favorite(UserRecipe):
    """Наследник абстрактного класса для избранного."""
    class Meta(UserRecipe.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(UserRecipe):
    """Наследник абстрактного класса для покупок."""
    class Meta(UserRecipe.Meta):
        default_related_name = 'cart'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
