from rest_framework import serializers

from recipes.models import (Ingredient, MeasureUnit, Recipe, RecipeIngredient,
                            Tag)


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


class RecipeSerializer(serializers.ModelSerializer):
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
