from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from .constants import HEX_COLOR_REGEX, STANDART_MAX_LENGTH, TEXT_LENGTH
from core.models import NameOrderingStr

User = get_user_model()


class Tag(NameOrderingStr):
    """
    Модель тэгов.
    Имеет поля name, color (проверяется regex на соответствие hex-color),
    slug.
    """
    color = models.CharField(unique=True,
                             validators=[RegexValidator(
                                 HEX_COLOR_REGEX,
                                 'Введите верное значение HEX-кода')],
                             verbose_name='цвет')
    slug = models.SlugField(max_length=STANDART_MAX_LENGTH,
                            unique=True)

    class Meta(NameOrderingStr.Meta):
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'


class MeasureUnit(NameOrderingStr):
    """Модель единиц измерения. Имеет поле name."""
    class Meta(NameOrderingStr.Meta):
        verbose_name = 'единица измерения'
        verbose_name_plural = 'единицы измерения'


class Ingredient(NameOrderingStr):
    """
    Модель ингредиентов.
    Имеет поля name, measurement_unit(внешний ключ к таблице MeasureUnit).
    При удалении единицы измерения, значение выставляется на null.
    """
    measurement_unit = models.ForeignKey(MeasureUnit,
                                         null=True,
                                         on_delete=models.SET_NULL,
                                         related_name='ingredients',
                                         verbose_name='единица измерения')

    class Meta(NameOrderingStr.Meta):
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'


class Recipe(NameOrderingStr):
    """
    Модель рецептов.
    Имеет поля name(название рецепта),
    ingredients(связь many-to-many к модели Ingredient),
    tags(связь many-to-many к модели Tag),
    image(картинка к рецепту),
    text(описание рецепта),
    cooking_time(время приготовления, должно быть >= 1),
    author(создатель рецепта, связь с моделью User),
    pub_date
    (время публикации рецепта, автоматически ставится текущее время и дата).
    """
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         related_name='recipes',
                                         verbose_name='ингредиент')
    tags = models.ManyToManyField(Tag,
                                  through='RecipeTag',
                                  related_name='recipes',
                                  verbose_name='тэг')
    image = models.ImageField(upload_to='recipes/images/',
                              verbose_name='картинка')
    text = models.TextField(verbose_name='описание')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='время приготовления в минутах')
    author = models.ForeignKey(User,
                               related_name='recipes',
                               on_delete=models.CASCADE,
                               verbose_name='автор')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='дата публикации')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'


class RecipeIngredient(models.Model):
    """
    Промежуточная модель для связи рецептов и ингредиентов.
    Имеет поле recipe(связь с моделью Recipe),
    ingredient(связь с моделью ingredient),
    amount(количество ингредиента для рецепта).
    """
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='рецепт')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name='ингредиент')
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='количество ингредиента')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('recipe', 'ingredient'),
                                    name='unique_recipe_ingredient')
        ]

    def __str__(self):

        return (f'{self.recipe.name[:TEXT_LENGTH]} '
                f'- {self.ingredient.name[:TEXT_LENGTH]} '
                f'в количестве {self.amount} '
                f'{self.ingredient.measurement_unit.name}')


class RecipeTag(models.Model):
    """
    Промежуточная модель для связи рецептов и тэгов.
    Имеет поле recipe(связь с моделью Recipe),
    tag(связь с моделью Tag).
    """
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='рецепт')
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            verbose_name='тэг')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('recipe', 'tag'),
                                    name='unique_recipe_tag')
        ]

    def __str__(self):

        return f'{self.recipe.name[:TEXT_LENGTH]} - {self.tag.name}'


class Favorite(models.Model):
    """
    Модель избранного.
    Имеет два поля: user(связь с моделью User),
    recipe(связь с моделью Recipe).
    """
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorites',
                             verbose_name='пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorites',
                               verbose_name='рецепт')

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранные'
        constraints = [
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='unique_favorite')
        ]

    def __str__(self):

        return (f'{self.user.username} '
                f'добавил в избранное рецепт "{self.recipe.name}"')


class ShoppingCart(models.Model):
    """
    Модель корзины покупок.
    Имеет два поля: user(связь с моделью User),
    recipe(связь с моделью Recipe).
    """
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shopping_cart',
                             verbose_name='пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='shopping_cart',
                               verbose_name='рецепт')

    class Meta:
        verbose_name = 'корзина покупок'
        verbose_name_plural = 'корзина покупок'
        constraints = [
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='unique_shopping_cart')
        ]

    def __str__(self):
        return (f'{self.user.username} '
                f'добавил в корзину покупок рецепт "{self.recipe.name}"')
