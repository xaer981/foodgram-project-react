from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .constants import EMAIL_MAX_LENGTH, NAME_PASS_MAX_LENGTH, USERNAME_REGEX


class CustomUser(AbstractUser):
    REQUIRED_FIELDS = ['username',
                       'first_name',
                       'last_name']
    USERNAME_FIELD = 'email'

    email = models.EmailField(max_length=EMAIL_MAX_LENGTH,
                              unique=True,
                              verbose_name='электронная почта')
    username = models.CharField(max_length=NAME_PASS_MAX_LENGTH,
                                unique=True,
                                validators=[RegexValidator(
                                    USERNAME_REGEX,
                                    'username содержит недопустимый символ')])
    first_name = models.CharField(max_length=NAME_PASS_MAX_LENGTH,
                                  verbose_name='имя')
    last_name = models.CharField(max_length=NAME_PASS_MAX_LENGTH,
                                 verbose_name='фамилия')
    password = models.CharField(max_length=NAME_PASS_MAX_LENGTH,
                                verbose_name='пароль')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('username',)


class Subscription(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name='subscriber')
    subscribing = models.ForeignKey(CustomUser,
                                    on_delete=models.CASCADE,
                                    related_name='subscribing')

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'subscribing'],
                                    name='unique_subscription')
        ]

    def __str__(self):

        return f'{self.user.username} подписан на {self.subscribing.username}'
