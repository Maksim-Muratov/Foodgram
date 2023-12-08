from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        'Email',
        max_length=254,
        unique=True,
        help_text='Обязательное поле. Не более 254 символов.'
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
        help_text='Обязательное поле. Не более 150 символов.'
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        help_text='Обязательное поле. Не более 150 символов.'
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        help_text='Обязательное поле. Не более 150 символов.'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username', 'first_name', 'last_name', 'password'
    ]

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_username()


class Subscribe(models.Model):
    """Модель подписки."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )

    class Meta:
        ordering = ['author__id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_subscribe'
            )
        ]

    def __str__(self):
        return f'Подписка {self.user} на {self.author}'
