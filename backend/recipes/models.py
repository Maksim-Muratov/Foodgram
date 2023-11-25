from django.db import models

from .validators import HexColorValidator


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

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
        return self.name


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField('Название', max_length=200, unique=True)
    color = models.CharField('HEX-цвет',
                             max_length=7,
                             unique=True,
                             validators=[HexColorValidator()])
    slug = models.SlugField('Slug', max_length=200, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
