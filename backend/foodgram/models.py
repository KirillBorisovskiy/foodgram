import secrets

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import (MinValueValidator, RegexValidator,
                                    validate_email)
from django.db import models

from foodgram import constants
from foodgram.validators import validate_username


class User(AbstractUser):
    username = models.CharField(
        max_length=constants.MAX_LENGHT_NAME,
        unique=True,
        verbose_name='Пользователь',
        validators=[
            RegexValidator(regex=constants.REGULAR_EXPRESSIONS),
            validate_username
        ]
    )
    email = models.EmailField(
        verbose_name='email адрес',
        validators=[validate_email],
        max_length=constants.MAX_LENGHT_EMAIL,
        unique=True
    )
    first_name = models.CharField(max_length=constants.MAX_LENGHT_NAME)
    last_name = models.CharField(max_length=constants.MAX_LENGHT_NAME)
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        blank=True,
        verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name="unique_fields"
            ),
        ]


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=constants.MAX_LENGHT_NAME,
        unique=True,
        db_index=True
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=constants.MEASUREMENT_LEN
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        max_length=constants.MAX_LENGHT_NAME,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=constants.MAX_LENGHT_NAME,
        verbose_name='Название рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    image = models.ImageField(
        upload_to='foodgram/images/',
        blank=True,
        null=True,
        default=None,
        verbose_name='Загрузить фото'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиент'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, 'Минимальное время приготовления')],
        verbose_name='Время приготовления',
        help_text='мин.'
    )
    short_url = models.CharField(
        max_length=constants.SHORT_URL_LEN,
        unique=True,
        blank=True,
        editable=False
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name

    def _generate_short_code(self):
        code = secrets.token_urlsafe(
            constants.SHORT_URL_LEN
        )[:constants.SHORT_URL_LEN]
        while Recipe.objects.filter(short_url=code).exists():
            code = secrets.token_urlsafe(
                constants.SHORT_URL_LEN
            )[:constants.SHORT_URL_LEN]
        return code

    def get_short_url(self, request):
        return request.build_absolute_uri(f'/s/{self.short_url}/')

    def save(self, *args, **kwargs):
        if not self.short_url:
            self.short_url = self._generate_short_code()
        super().save(*args, **kwargs)


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        verbose_name='Название рецепта',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Укажите количество ингредиента'
    )

    class Meta:
        verbose_name = 'Cостав рецепта'
        verbose_name_plural = 'Состав рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredients'
            )]

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_carts'
    )


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
