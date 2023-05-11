from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .utils import Base64ImageField
from recipes.models import (Ingredient, MeasureUnit, Recipe, RecipeIngredient,
                            RecipeTag, Tag)


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.SlugRelatedField(
        slug_field='name',
        queryset=MeasureUnit.objects.all())

    class Meta:
        model = Ingredient
        fields = ('id',
                  'name',
                  'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id',
                  'name',
                  'color',
                  'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
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


class RecipeGETSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'ingredients',
                  'name',
                  'image',
                  'text',
                  'cooking_time')

    def get_ingredients(self, recipe):
        ingredients = RecipeIngredient.objects.filter(recipe=recipe)

        return RecipeIngredientSerializer(ingredients, many=True).data


class IngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(slug_field='id',
                                        queryset=Tag.objects.all(),
                                        many=True)
    ingredients = IngredientToRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'ingredients',
                  'name',
                  'image',
                  'text',
                  'cooking_time')

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for i in ingredients:
            ingredient = get_object_or_404(Ingredient,
                                           id=i['id'])
            RecipeIngredient.objects.create(recipe=recipe,
                                            ingredient=ingredient,
                                            amount=i['amount'])

        for tag in tags:
            RecipeTag.objects.create(recipe=recipe,
                                     tag=tag)

        return recipe

    def to_representation(self, instance):
        return RecipeGETSerializer(instance)
