from django.db import transaction
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .validators import ingredients_tags_in_recipe_validator
from recipes.models import (Favorite, Ingredient, MeasureUnit, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import CustomUser as User
from users.models import Subscription


class CustomUserSerializer(UserSerializer):
    """
    Кастомный сериализатор,
    унаследованный от стандартного UserSerializer Djoser'а.
    Дополнительно выводит поле с информацией
    о наличии/отсутствии подписки на просматриваемого юзера.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:

            return False

        return Subscription.objects.filter(user=user, subscribing=obj).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Нельзя добавить рецепт в избранное дважды!')
        ]


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient.
    measurement_unit для вызванного ингредиента
    получает из таблица MeasureUnit.
    """
    measurement_unit = serializers.SlugRelatedField(
        slug_field='name',
        queryset=MeasureUnit.objects.all())

    class Meta:
        model = Ingredient
        fields = ('id',
                  'name',
                  'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Tag.
    Проверяет цвет на соответствие HEX-коду.
    Проверка цвета подтягивается из модели.
    """
    class Meta:
        model = Tag
        fields = ('id',
                  'name',
                  'color',
                  'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели RecipeIngredient.
    Берёт информацию из связанных таблицы Ingredient и MeasureUnit.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit.name')

    class Meta:
        model = RecipeIngredient
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Recipe.
    Поле image преобразовывает полученный base64 в картинку.
    Проверяет тэги и ингредиенты,
    а также правильно создаёт/обновляет m2m связи объекта.
    """
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True,
        read_only=True
    )
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')

        ingredients_tags_in_recipe_validator(ingredients, tags)

        data['ingredients'] = ingredients
        data['tags'] = tags

        return data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:

            return False

        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:

            return False

        return user.shopping_cart.filter(recipe=obj).exists()

    @transaction.atomic
    def create_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(recipe=recipe,
                             ingredient_id=ingredient.get('id'),
                             amount=ingredient.get('amount'))
            for ingredient in ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)

        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = super().update(recipe, validated_data)
        recipe.tags.clear()
        recipe.tags.set(tags)
        recipe.ingredients.clear()
        self.create_ingredients(ingredients, recipe)
        recipe.save()

        return recipe


class RecipeShortSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткого представления модели Recipe.
    Используется в других сериализаторах.
    """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор ShoppingCart.
    Поля связаны через PK с User и Recipe.
    Проверяет, что рецепт не добавляется в ShoppingCart дважды.
    """
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Нельзя добавить рецепт в корзину покупок дважды!'
            )
        ]


class SubscriptionListSerializer(CustomUserSerializer):
    """
    Сериализатор представления Subsciption.
    Подтягивает количество рецептов и сами рецепты юзера,
    на которого подписались.
    """
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('recipes',
                                                     'recipes_count')
        read_only_fields = ('email',
                            'username',
                            'first_name',
                            'last_name')

    def get_recipes_count(self, obj):

        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)

        return serializer.data


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор записи Subscription.
    Проверяет, что пользователь не был подписан ранее
    и не подписывается на себя же.
    При представлении возвращает SubscriptionListSerializer.
    """

    class Meta:
        model = Subscription
        fields = ('user', 'subscribing')
        validators = [
            UniqueTogetherValidator(queryset=Subscription.objects.all(),
                                    fields=('user', 'subscribing'),
                                    message='Вы уже подписаны!')
        ]

    def validate(self, data):
        subscribing = data.get('subscribing')
        user = self.context.get('request').user

        if user == subscribing:
            raise serializers.ValidationError('Нельзя подписаться на себя.')

        return data

    def to_representation(self, instance):

        return SubscriptionListSerializer(
            instance.subscribing,
            context={'request': self.context.get('request')}).data
