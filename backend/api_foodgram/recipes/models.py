from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from .constants import HEX_COLOR_REGEX, STANDART_MAX_LENGTH, TEXT_LENGTH


class NameOrderingStr(models.Model):
    """
    Абстрактная модель с полем name,
    сортировкой по этому полю и возвратом этого поля при вызове str.
    """
    name = models.CharField(max_length=STANDART_MAX_LENGTH,
                            unique=True,
                            verbose_name='название')

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):

        return self.name[:TEXT_LENGTH]


class Tag(NameOrderingStr):
    """
    Модель тэгов.
    Имеет поля name, color (проверяется regex на соответствие hex-color),
    slug.
    """
    color = models.CharField(unique=True,
                             validators=[RegexValidator(HEX_COLOR_REGEX)],
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
    Имеет поля ingredients(связь many-to-many к модели Ingredient),
    tags(связь many-to-many к модели Tag),
    image(картинка к рецепту),
    text(описание рецепта),
    cooking_time(время приготовления, должно быть >= 1),
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
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='дата публикации')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='количество ингредиента')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('recipe', 'ingredient'),
                                    name='unique_recipe_ingredient')
        ]

    def __str__(self):

        return (f'{self.recipe} - {self.ingredient} '
                f'в количестве {self.amount} '
                f'{self.ingredient.measurement_unit}')


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('recipe', 'tag'),
                                    name='unique_recipe_tag')
        ]

    def __str__(self):

        return f'{self.recipe} - {self.tag}'
