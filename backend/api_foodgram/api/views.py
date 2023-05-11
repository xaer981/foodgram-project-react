from rest_framework import viewsets

from .serializers import (IngredientSerializer, RecipeGETSerializer,
                          RecipeSerializer, TagSerializer)
from recipes.models import Ingredient, Recipe, Tag


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.prefetch_related('tags', 'ingredients')

    def get_serializer_class(self):
        if self.request.method == 'GET':

            return RecipeGETSerializer

        return RecipeSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
