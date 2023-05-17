from django.db import models

from recipes.constants import STANDART_MAX_LENGTH, TEXT_LENGTH


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
